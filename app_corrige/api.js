// ============================================================
// api.js - API Client avec Gestion des Conflits
// ============================================================

const API = {
    // ============================================================
    // ÉTAT
    // ============================================================
    _token: null,
    _tokenExpire: null,
    _version: 0,

    // ============================================================
    // AUTHENTIFICATION - SUPPRIMÉE
    // ============================================================
    // Les fonctions login, _getToken, _getHeaders, _isAuthenticated
    // ont été modifiées pour ne plus utiliser l'authentification

    _getHeaders() {
        // L'authentification a été supprimée
        // On retourne juste les headers de base
        return { 'Content-Type': 'application/json' };
    },

    _isAuthenticated() {
        // L'authentification a été supprimée - toujours authentifié
        return true;
    },

    // ============================================================
    // FONCTIONS DE BASE (avec gestion d'erreurs améliorée)
    // ============================================================
    async load(cle) {
        try {
            const headers = this._getHeaders();
            const response = await fetch('/load', { headers });
            
            // La vérification d'authentification a été supprimée
            
            if (!response.ok) throw new Error(`HTTP ${response.status} - ${response.statusText}`);
            
            const data = await response.json();
            if (data.status === 'success') {
                // Récupérer la version PROPRE À CETTE CLÉ
                if (data._versions && data._versions[cle] !== undefined) {
                    localStorage.setItem(`${cle}_version`, data._versions[cle].toString());
                }
                // Extraire les données demandées
                const result = data[cle] !== undefined ? data[cle] : null;
                // Mettre en cache local
                if (result !== null) {
                    localStorage.setItem(cle, JSON.stringify(result));
                }
                return result;
            }
            
            // Fallback: essayer localStorage
            const locale = localStorage.getItem(cle);
            if (locale) {
                try {
                    const data = JSON.parse(locale);
                    console.warn("⚠️ Données chargées depuis le cache local (hors-ligne)");
                    this._notifier(`📶 Mode hors-ligne - Données chargées depuis le cache`, 'warning');
                    return data;
                } catch(e) { 
                    console.error("Erreur de parsing localStorage:", e);
                }
            }
            
            this._notifier(`❌ Erreur de chargement`, 'error');
            return null;
            
        } catch (erreur) {
            console.error("❌ Erreur load:", erreur.message);
            
            // Essayer de charger depuis localStorage
            const locale = localStorage.getItem(cle);
            if (locale) {
                try {
                    const data = JSON.parse(locale);
                    console.warn("⚠️ Données chargées depuis le cache local (hors-ligne)");
                    this._notifier(`📶 Mode hors-ligne - Données chargées depuis le cache`, 'warning');
                    return data;
                } catch(e) { 
                    console.error("Erreur de parsing localStorage:", e);
                }
            }
            
            this._notifier(`❌ Erreur de chargement : ${erreur.message}`, 'error');
            return null;
        }
    },

    async save(cle, valeur) {
        try {
            // Sauvegarde locale d'abord (pour le mode hors-ligne)
            localStorage.setItem(cle, JSON.stringify(valeur));
            
            // Récupérer la version locale
            const versionLocale = parseInt(localStorage.getItem(`${cle}_version`) || '0');
            
            const payload = {};
            payload[cle] = valeur;
            payload['_version'] = versionLocale + 1;
            
            const headers = this._getHeaders();
            const response = await fetch('/save', {
                method: 'POST',
                headers: headers,
                body: JSON.stringify(payload)
            });
            
            // La vérification d'authentification a été supprimée
            
            const data = await response.json();
            
            if (data.status === 'conflict') {
                // Conflit de version
                const choix = await this._dialogConfirm(
                    `⚠️ Conflit de version détecté !\n\n` +
                    `Version serveur : ${data.version_serveur}\n` +
                    `Version locale : ${versionLocale}\n\n` +
                    `Voulez-vous charger la version du serveur ?`
                );
                
                if (choix) {
                    // Charger la version serveur
                    const versionServeur = await this.load(cle);
                    this._notifier(`📥 Données chargées depuis le serveur`, 'info');
                    return false;
                } else {
                    // Forcer la sauvegarde (avec nouvelle version)
                    this._notifier(`⚠️ Sauvegarde forcée (conflit ignoré)`, 'warning');
                    // Réessayer avec une version plus haute
                    payload['_version'] = data.version_serveur + 1;
                    const retryResponse = await fetch('/save', {
                        method: 'POST',
                        headers: headers,
                        body: JSON.stringify(payload)
                    });
                    if (retryResponse.ok) {
                        const retryData = await retryResponse.json();
                        if (retryData.version) {
                            localStorage.setItem(`${cle}_version`, retryData.version.toString());
                        }
                        this._notifier(`💾 Données sauvegardées avec succès (conflit résolu)`, 'success');
                        return true;
                    }
                    return false;
                }
            }
            
            if (response.ok) {
                if (data.version) {
                    localStorage.setItem(`${cle}_version`, data.version.toString());
                }
                console.log(`✅ Sauvegardé: ${cle}`);
                this._notifier(`💾 Données sauvegardées avec succès`, 'success');
                return true;
            }
            
            throw new Error(`HTTP ${response.status}`);
            
        } catch (erreur) {
            console.error("❌ Erreur save:", erreur.message);
            this._notifier(`⚠️ Sauvegarde locale uniquement (serveur indisponible)`, 'warning');
            this._tentativeDifferee(cle, valeur);
            return false;
        }
    },

    // ============================================================
    // DIALOGUE PERSONNALISÉ (remplace confirm/alert)
    // ============================================================
    _dialogConfirm(message) {
        return new Promise((resolve) => {
            // Créer une modale temporaire
            const overlay = document.createElement('div');
            overlay.style.cssText = `
                position: fixed;
                top: 0; left: 0; right: 0; bottom: 0;
                background: rgba(0,0,0,0.5);
                backdrop-filter: blur(4px);
                z-index: 9999;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            `;
            
            const modal = document.createElement('div');
            modal.style.cssText = `
                background: white;
                border-radius: 16px;
                padding: 30px;
                max-width: 450px;
                width: 100%;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                animation: modalIn 0.3s ease-out;
            `;
            
            modal.innerHTML = `
                <h3 style="margin-top:0;font-size:20px;color:#1a1a2e;">Confirmation</h3>
                <p style="white-space:pre-line;color:#495057;font-size:15px;line-height:1.6;">${message}</p>
                <div style="display:flex;gap:12px;margin-top:24px;flex-wrap:wrap;">
                    <button id="dialogCancel" style="flex:1;padding:12px;border:2px solid #dee2e6;border-radius:10px;background:transparent;font-weight:600;font-size:15px;cursor:pointer;font-family:inherit;">Annuler</button>
                    <button id="dialogConfirm" style="flex:1;padding:12px;border:none;border-radius:10px;background:#6f42c1;color:white;font-weight:600;font-size:15px;cursor:pointer;font-family:inherit;">Confirmer</button>
                </div>
            `;
            
            overlay.appendChild(modal);
            document.body.appendChild(overlay);
            
            document.getElementById('dialogConfirm').onclick = () => {
                document.body.removeChild(overlay);
                resolve(true);
            };
            document.getElementById('dialogCancel').onclick = () => {
                document.body.removeChild(overlay);
                resolve(false);
            };
            overlay.onclick = (e) => {
                if (e.target === overlay) {
                    document.body.removeChild(overlay);
                    resolve(false);
                }
            };
            
            // Ajouter l'animation
            const style = document.createElement('style');
            style.textContent = `
                @keyframes modalIn {
                    from { opacity: 0; transform: scale(0.95) translateY(10px); }
                    to { opacity: 1; transform: scale(1) translateY(0); }
                }
            `;
            document.head.appendChild(style);
        });
    },

    // ============================================================
    // NOTIFICATIONS UTILISATEUR
    // ============================================================
    _notifier(message, type = 'info') {
        let notif = document.getElementById('api-notification');
        if (!notif) {
            notif = document.createElement('div');
            notif.id = 'api-notification';
            notif.style.cssText = `
                position: fixed;
                bottom: 30px;
                right: 30px;
                z-index: 9998;
                padding: 14px 24px;
                border-radius: 12px;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                font-size: 14px;
                font-weight: 500;
                max-width: 420px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.15);
                transition: all 0.4s ease;
                opacity: 0;
                transform: translateY(20px) scale(0.95);
                pointer-events: none;
                display: flex;
                align-items: center;
                gap: 10px;
            `;
            document.body.appendChild(notif);
        }
        
        const colors = {
            success: { bg: '#d4edda', border: '#28a745', text: '#155724', icon: '✅' },
            warning: { bg: '#fff3cd', border: '#fd7e14', text: '#856404', icon: '⚠️' },
            error: { bg: '#f8d7da', border: '#dc3545', text: '#721c24', icon: '❌' },
            info: { bg: '#cce5ff', border: '#007bff', text: '#004085', icon: 'ℹ️' }
        };
        
        const style = colors[type] || colors.info;
        notif.style.background = style.bg;
        notif.style.borderLeft = `4px solid ${style.border}`;
        notif.style.color = style.text;
        notif.innerHTML = `<span>${style.icon}</span> ${message}`;
        
        // Afficher
        notif.style.opacity = '1';
        notif.style.transform = 'translateY(0) scale(1)';
        notif.style.pointerEvents = 'auto';
        
        clearTimeout(notif._timer);
        notif._timer = setTimeout(() => {
            notif.style.opacity = '0';
            notif.style.transform = 'translateY(20px) scale(0.95)';
            notif.style.pointerEvents = 'none';
        }, 6000);
    },

    // ============================================================
    // TENTATIVE DE SAUVEGARDE DIFFÉRÉE
    // ============================================================
    _tentativeDifferee(cle, valeur, tentatives = 0, force = false) {
        const maxTentatives = 5;
        const delai = 30000;
        
        if (tentatives >= maxTentatives) {
            console.warn(`⚠️ Sauvegarde abandonnée après ${maxTentatives} tentatives`);
            this._notifier(`⚠️ Sauvegarde impossible - Vérifiez votre connexion`, 'error');
            return;
        }
        
        setTimeout(async () => {
            try {
                const versionLocale = parseInt(localStorage.getItem(`${cle}_version`) || '0');
                const payload = {};
                payload[cle] = valeur;
                payload['_version'] = versionLocale + 1;
                
                const headers = this._getHeaders();
                const response = await fetch('/save', {
                    method: 'POST',
                    headers: headers,
                    body: JSON.stringify(payload)
                });
                
                if (response.ok) {
                    const data = await response.json();
                    if (data.version) {
                        localStorage.setItem(`${cle}_version`, data.version.toString());
                    }
                    console.log(`✅ Sauvegarde différée réussie pour: ${cle}`);
                    this._notifier(`💾 Données synchronisées avec le serveur`, 'success');
                    return;
                }
                // Échec, réessayer
                this._tentativeDifferee(cle, valeur, tentatives + 1);
            } catch (e) {
                console.warn(`⚠️ Tentative ${tentatives + 1} échouée, nouvelle tentative dans ${delai/1000}s`);
                this._tentativeDifferee(cle, valeur, tentatives + 1);
            }
        }, delai);
    },

    // ============================================================
    // EXPORT / IMPORT COMPLET DES DONNÉES
    // ============================================================
    async exporterToutesDonnees() {
        try {
            const headers = this._getHeaders();
            const response = await fetch('/load', { headers });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const data = await response.json();
            
            const exportData = {
                version: 1.0,
                exportDate: new Date().toISOString(),
                donnees: data,
                totalEleves: Object.values(data.all_eleves?.donnees || {}).reduce((sum, n) => 
                    sum + (n.eleves?.length || 0), 0
                )
            };
            
            const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `sauvegarde_plateforme_${new Date().toISOString().slice(0,10)}.json`;
            a.click();
            URL.revokeObjectURL(url);
            
            this._notifier(`💾 Données exportées (${exportData.totalEleves} élèves)`, 'success');
            return true;
        } catch (e) {
            console.error('Erreur export:', e);
            this._notifier(`❌ Erreur export: ${e.message}`, 'error');
            return false;
        }
    },

    async importerToutesDonnees(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = async (e) => {
                try {
                    const data = JSON.parse(e.target.result);
                    if (!data.donnees) {
                        throw new Error('Format invalide');
                    }
                    
                    // Sauvegarder les données
                    for (const [cle, valeur] of Object.entries(data.donnees)) {
                        await this.save(cle, valeur);
                    }
                    
                    this._notifier(`✅ Importation réussie`, 'success');
                    resolve(true);
                } catch (err) {
                    this._notifier(`❌ Erreur import: ${err.message}`, 'error');
                    reject(err);
                }
            };
            reader.readAsText(file);
        });
    },

    // ============================================================
    // SERVICES PHOTOS
    // ============================================================
    Photos: {
        async upload(niveau, id, file) {
            try {
                const formData = new FormData();
                formData.append('niveau', niveau);
                formData.append('id', id);
                formData.append('photo', file);
                
                // L'authentification a été supprimée
                const response = await fetch('/photo', {
                    method: 'POST',
                    body: formData
                });
                
                // La vérification d'authentification a été supprimée
                
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                const result = await response.json();
                API._notifier(`📸 Photo importée avec succès`, 'success');
                return result;
            } catch (erreur) {
                console.error("❌ Erreur upload photo:", erreur);
                API._notifier(`❌ Erreur lors de l'import de la photo`, 'error');
                throw erreur;
            }
        },

        async get(niveau, id) {
            try {
                // L'authentification a été supprimée
                const response = await fetch(`/photo?niveau=${encodeURIComponent(niveau)}&id=${id}`);
                if (!response.ok) {
                    if (response.status === 404) return null;
                    throw new Error(`HTTP ${response.status}`);
                }
                return await response.blob();
            } catch (erreur) {
                console.error("❌ Erreur get photo:", erreur);
                return null;
            }
        },

        async delete(niveau, id) {
            try {
                // L'authentification a été supprimée
                const response = await fetch(`/photo?niveau=${encodeURIComponent(niveau)}&id=${id}`, {
                    method: 'DELETE'
                });
                // La vérification d'authentification a été supprimée
                if (response.ok) {
                    API._notifier(`🗑️ Photo supprimée`, 'success');
                }
                return response.ok;
            } catch (erreur) {
                console.error("❌ Erreur delete photo:", erreur);
                API._notifier(`❌ Erreur lors de la suppression`, 'error');
                return false;
            }
        }
    },

    // ============================================================
    // SERVICES DÉCLENCHEURS
    // ============================================================
    Triggers: {
        genererGroupe(declencheurs, modeQCM = false) {
            let html = '';
            declencheurs.forEach((item) => {
                const bonneAttr = item.bonne ? ' data-bonne="true"' : '';
                const styleAttr = item.style || 'popup';
                const questionAttr = (item.texte || '').replace(/"/g, '&quot;');
                const contenuAttr = (item.contenu || '').replace(/"/g, '&quot;');
                
                let styleAttribs = '';
                if (item.tStyle) {
                    if (item.tStyle.tColor) styleAttribs += ` data-t-color="${item.tStyle.tColor}"`;
                    if (item.tStyle.tSize) styleAttribs += ` data-t-size="${item.tStyle.tSize}"`;
                    if (item.tStyle.tFont) styleAttribs += ` data-t-font="${item.tStyle.tFont}"`;
                    if (item.tStyle.tBold) styleAttribs += ` data-t-bold="true"`;
                    if (item.tStyle.tItalic) styleAttribs += ` data-t-italic="true"`;
                    if (item.tStyle.tUnderline) styleAttribs += ` data-t-underline="true"`;
                }

                const icone = modeQCM ? '📋 ' : '💡 ';
                let libelle = item.texte || 'Cliquez ici';
                if (libelle.length > 60) libelle = libelle.substring(0, 60) + '…';

                html += `<span class="trigger-element" data-type="reponse" data-contenu="${contenuAttr}" data-style="${styleAttr}" data-question="${questionAttr}"${bonneAttr}${styleAttribs}>${icone}${libelle}<span class="trigger-badge">🔗</span></span> `;
            });

            const modeQCMAttr = modeQCM ? ' data-qcm="true"' : '';
            return `<span class="trigger-group"${modeQCMAttr}>${html}</span>`;
        }
    },

    // ============================================================
    // FONCTIONS UTILITAIRES
    // ============================================================
    Utils: {
        generateId() {
            return Date.now().toString(36) + Math.random().toString(36).substr(2, 5);
        },

        getCleSeances(niveau, trimestre, module) {
            return `donnees_seances_${niveau.replace(/\s+/g, '_')}__${trimestre.replace(/\s+/g, '_')}__${module.replace(/\s+/g, '_')}`;
        },

        autoSave(cle, valeur, delay = 500) {
            clearTimeout(this._timer);
            this._timer = setTimeout(() => {
                API.save(cle, valeur);
            }, delay);
        }
    }
};

// ============================================================
// FONCTIONS DE COMPATIBILITÉ (pour les scripts existants)
// ============================================================
async function chargerDonneesServeur(cle) { 
    return await API.load(cle); 
}

async function sauvegarderDonneesServeur(cle, valeur) { 
    return await API.save(cle, valeur); 
}

// ============================================================
// INITIALISATION
// ============================================================
// L'initialisation du token a été supprimée car plus nécessaire