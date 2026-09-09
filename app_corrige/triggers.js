// ============================================================
// triggers.js - Gestion unifiée des déclencheurs
// ============================================================

const Triggers = {
    // ============================================================
    // CONSTANTES
    // ============================================================
    STYLES: `
        /* ===== DECLENCHEURS ===== */
        .trigger-group {
            display: inline;
            border: none;
            padding: 0;
            background: transparent;
            margin: 0;
        }

        /* Mode QCM en colonne */
        .trigger-group[data-qcm="true"] {
            display: flex;
            flex-direction: column;
            gap: 10px;
            width: 100%;
            max-width: 700px;
            margin: 12px auto;
            padding: 6px 0;
        }

        .trigger-group[data-qcm="true"] .trigger-element {
            display: block !important;
            padding: 14px 20px;
            border: 2px solid #dee2e6;
            border-radius: 10px;
            background: #f8f9fa;
            cursor: pointer;
            text-align: left;
            font-size: 0.9em;
            transition: all 0.2s;
            width: 100%;
            margin: 0 !important;
            text-decoration: none !important;
            font-weight: 500;
            color: #1a1a2e !important;
        }

        .trigger-group[data-qcm="true"] .trigger-element:hover {
            background: #e9ecef;
            border-color: #6f42c1;
            transform: scale(1.01);
        }

        .trigger-group[data-qcm="true"] .trigger-element.qcm-correct {
            border-color: #28a745;
            background: #d4edda;
            color: #155724;
        }

        .trigger-group[data-qcm="true"] .trigger-element.qcm-incorrect {
            border-color: #dc3545;
            background: #f8d7da;
            color: #721c24;
            opacity: 0.85;
        }

        .trigger-group[data-qcm="true"] .trigger-element .trigger-badge {
            display: none;
        }

        .trigger-group[data-qcm="true"] .trigger-element.selected {
            border-color: #6f42c1;
            background: #e7f3ff;
            font-weight: 600;
            transform: scale(1.02);
        }

        /* ===== DECLENCHEURS NORMAUX (NON-QCM) EN COLONNE ===== */
        .trigger-group:not([data-qcm="true"]) {
            display: flex !important;
            flex-direction: column !important;
            gap: 8px !important;
            width: 100% !important;
            max-width: 600px !important;
            margin: 12px auto !important;
            padding: 6px 0 !important;
        }

        .trigger-group:not([data-qcm="true"]) .trigger-element {
            display: block !important;
            padding: 12px 18px !important;
            border: 2px solid #dee2e6 !important;
            border-radius: 10px !important;
            background: #f8f9fa !important;
            cursor: pointer !important;
            text-align: left !important;
            font-size: 0.9em !important;
            transition: all 0.2s !important;
            width: 100% !important;
            margin: 0 !important;
            text-decoration: none !important;
            color: #1a1a2e !important;
        }

        .trigger-group:not([data-qcm="true"]) .trigger-element:hover {
            background: #e9ecef !important;
            border-color: #6f42c1 !important;
            transform: scale(1.01);
        }

        .trigger-group:not([data-qcm="true"]) .trigger-element .trigger-badge {
            display: none !important;
        }

        /* ============================================================
           STYLES POUR LE MODE PRÉSENTATION (diaporama)
           ============================================================ */
        /* En mode présentation (sans .trigger-editor) : */
        /* La question est visible en ligne */
        .trigger-group .trigger-element[data-type="question"] {
            display: inline-block !important;
            background: transparent !important;
            border: none !important;
            padding: 0 4px !important;
            text-decoration: underline !important;
            text-decoration-color: #6f42c1 !important;
            text-underline-offset: 4px !important;
            text-decoration-thickness: 2px !important;
            color: #1a1a2e !important;
            font-weight: normal !important;
            margin: 0 2px !important;
            cursor: pointer !important;
        }

        .trigger-group .trigger-element[data-type="question"] .trigger-badge {
            display: inline !important;
            font-size: 10px !important;
            background: #6f42c1 !important;
            color: white !important;
            border-radius: 10px !important;
            padding: 0 6px !important;
            margin-left: 4px !important;
        }

        /* Les réponses (data-type="reponse") sont cachées par défaut dans le diaporama */
        .trigger-group .trigger-element[data-type="reponse"] {
            display: none !important;
        }

        /* Quand les réponses sont révélées dans le diaporama, elles s'affichent en colonne */
        .trigger-group.reponses-visible .trigger-element[data-type="reponse"] {
            display: block !important;
            padding: 12px 18px !important;
            border: 2px solid #dee2e6 !important;
            border-radius: 10px !important;
            background: #f8f9fa !important;
            text-align: left !important;
            font-size: 0.9em !important;
            transition: all 0.2s !important;
            width: 100% !important;
            margin: 0 !important;
            text-decoration: none !important;
            color: #1a1a2e !important;
        }

        .trigger-group.reponses-visible .trigger-element[data-type="reponse"]:hover {
            background: #e9ecef !important;
            border-color: #6f42c1 !important;
            transform: scale(1.01);
        }

        /* En mode QCM en présentation, tout est visible */
        .trigger-group[data-qcm="true"] .trigger-element {
            display: block !important;
        }

        .trigger-group[data-qcm="true"] .trigger-element[data-type="question"] {
            display: block !important;
            text-decoration: none !important;
            font-weight: 500 !important;
            padding: 14px 20px !important;
            border: 2px solid #dee2e6 !important;
            border-radius: 10px !important;
            background: #f8f9fa !important;
            text-align: left !important;
            font-size: 0.9em !important;
        }

        .trigger-group[data-qcm="true"] .trigger-element[data-type="question"] .trigger-badge {
            display: none !important;
        }

        .trigger-group[data-qcm="true"] .trigger-element .trigger-badge {
            display: none !important;
        }

        /* ============================================================
           STYLES POUR L'ÉDITEUR - RÉPONSES TOUJOURS VISIBLES
           ============================================================ */

        /* Dans l'éditeur, la question s'affiche comme un bloc stylisé */
        .trigger-editor.trigger-group .trigger-element[data-type="question"],
        .trigger-editor .trigger-element[data-type="question"] {
            background: #e7f3ff !important;
            border: 2px solid #6f42c1 !important;
            border-radius: 8px !important;
            padding: 10px 16px !important;
            cursor: pointer !important;
            display: block !important;
            margin: 4px 0 !important;
            color: #1a1a2e !important;
            font-weight: 600 !important;
            font-size: 16px !important;
            text-decoration: none !important;
        }
        .trigger-editor.trigger-group .trigger-element[data-type="question"] .trigger-badge,
        .trigger-editor .trigger-element[data-type="question"] .trigger-badge {
            display: none !important;
        }

        /* Dans l'éditeur, les réponses sont TOUJOURS VISIBLES en colonne,
           sous la question correspondante (indentées) */
        .trigger-editor.trigger-group .trigger-element[data-type="reponse"],
        .trigger-editor .trigger-element[data-type="reponse"] {
            display: block !important;
            background: #f0f8f0 !important;
            border: 2px solid #28a745 !important;
            border-radius: 8px !important;
            padding: 8px 14px !important;
            margin: 4px 0 !important;
            margin-left: 20px !important;
            color: #155724 !important;
            font-weight: 500 !important;
            font-size: 14px !important;
            cursor: pointer !important;
            text-decoration: none !important;
            width: auto !important;
        }
        .trigger-editor.trigger-group .trigger-element[data-type="reponse"] .trigger-badge,
        .trigger-editor .trigger-element[data-type="reponse"] .trigger-badge {
            display: none !important;
        }

        /* Dans l'éditeur, mode QCM : les éléments sont en colonne */
        .trigger-editor.trigger-group[data-qcm="true"] .trigger-element,
        .trigger-editor .trigger-element[data-qcm="true"] {
            display: block !important;
            margin: 4px 0 !important;
        }
        .trigger-editor.trigger-group[data-qcm="true"] .trigger-element .trigger-badge,
        .trigger-editor .trigger-element[data-qcm="true"] .trigger-badge {
            display: none !important;
        }

        /* Éléments sélectionnés dans l'éditeur */
        .trigger-element.selected {
            font-size: 1.1em;
            background: transparent;
            border: none;
            padding: 0 4px;
            z-index: 2;
            font-weight: 600;
            color: #6f42c1;
        }
        .trigger-element:hover { 
            background: transparent;
            color: #5a32a3;
        }
        .trigger-element .trigger-badge {
            display: none;
        }

        .trigger-element.qcm-correct {
            background: transparent !important;
            border: none !important;
            color: #28a745 !important;
            font-weight: 600;
        }
        .trigger-element.qcm-incorrect {
            background: transparent !important;
            border: none !important;
            color: #dc3545 !important;
            text-decoration: line-through !important;
            opacity: 0.7;
        }

        .trigger-response {
            margin-top: 10px;
            padding: 14px 18px;
            background: #f8f9fa;
            color: #1a1a2e;
            border-radius: 10px;
            border-left: 4px solid #6f42c1;
            text-align: left;
        }
        .trigger-response img { max-width: 100%; height: auto; border-radius: 8px; }
    `,

    // ============================================================
    // INJECTION DES STYLES
    // ============================================================
    injectStyles: function(containerSelector) {
        if (!document.getElementById('triggers-common-styles')) {
            const style = document.createElement('style');
            style.id = 'triggers-common-styles';
            style.textContent = this.STYLES;
            document.head.appendChild(style);
        }

        if (containerSelector) {
            const container = document.querySelector(containerSelector);
            if (container) {
                // Ajouter la classe au conteneur
                container.classList.add('trigger-editor');
                
                // Ajouter la classe à tous les groupes existants
                container.querySelectorAll('.trigger-group').forEach(function(group) {
                    group.classList.add('trigger-editor');
                });
                
                // Utiliser MutationObserver pour les futurs groupes
                if (window.MutationObserver) {
                    // Supprimer l'observateur précédent s'il existe
                    if (container._triggerObserver) {
                        container._triggerObserver.disconnect();
                    }
                    
                    var observer = new MutationObserver(function() {
                        container.querySelectorAll('.trigger-group:not(.trigger-editor)').forEach(function(group) {
                            group.classList.add('trigger-editor');
                        });
                    });
                    observer.observe(container, { childList: true, subtree: true });
                    container._triggerObserver = observer;
                }
            }
        }
    },

    // ============================================================
    // EXTRAIRE LES DÉCLENCHEURS D'UN CONTENEUR
    // ============================================================
    extraire: function(container) {
        const declencheurs = [];
        const elements = container.querySelectorAll('.trigger-element');
        elements.forEach(el => {
            const contenu = el.dataset.contenu || '';
            const bonne = el.dataset.bonne === 'true';
            const question = el.dataset.question || el.textContent.replace(/[💡🔗📋✅❌]/g, '').trim();
            const type = el.dataset.type || 'reponse';
            const style = el.dataset.style || 'popup';
            
            // #7 : isQuestion basé sur data-type
            const isQuestion = (type === 'question') || (el.dataset.isQuestion === 'true');
            
            declencheurs.push({
                element: el,
                contenu: contenu,
                bonne: bonne,
                question: question,
                type: type,
                style: style,
                isQuestion: isQuestion,  // #7
                affiche: false,
                tStyle: {
                    tColor: el.dataset.tColor || '#007bff',
                    tSize: el.dataset.tSize || '18',
                    tFont: el.dataset.tFont || '',
                    tBold: el.dataset.tBold === 'true',
                    tItalic: el.dataset.tItalic === 'true',
                    tUnderline: el.dataset.tUnderline === 'true'
                }
            });
        });
        return declencheurs;
    },

    // ============================================================
    // #7 : GÉNÉRER UN GROUPE DE DÉCLENCHEURS (avec isQuestion)
    // ============================================================
    genererGroupe: function(declencheurs, modeQCM = false) {
        let html = '';
        declencheurs.forEach((item) => {
            // #7 : utiliser isQuestion au lieu de l'index
            const isQuestion = item.isQuestion === true;
            const dataType = isQuestion ? 'question' : 'reponse';
            
            const bonneAttr = item.bonne ? ' data-bonne="true"' : '';
            const styleAttr = item.style || 'popup';
            const typeAttr = item.type || 'reponse';
            const questionAttr = (item.texte || item.question || '').replace(/"/g, '&quot;');
            const contenuAttr = (item.contenu || '').replace(/"/g, '&quot;');
            const isQuestionAttr = isQuestion ? ' data-is-question="true"' : '';

            let styleAttribs = '';
            if (item.tStyle) {
                if (item.tStyle.tColor) styleAttribs += ` data-t-color="${item.tStyle.tColor}"`;
                if (item.tStyle.tSize) styleAttribs += ` data-t-size="${item.tStyle.tSize}"`;
                if (item.tStyle.tFont) styleAttribs += ` data-t-font="${item.tStyle.tFont}"`;
                if (item.tStyle.tBold) styleAttribs += ` data-t-bold="true"`;
                if (item.tStyle.tItalic) styleAttribs += ` data-t-italic="true"`;
                if (item.tStyle.tUnderline) styleAttribs += ` data-t-underline="true"`;
            }

            // ============================================================
            // CORRECTION : Pour les réponses, afficher data-contenu au lieu de data-question
            // ============================================================
            let libelle;
            if (isQuestion) {
                // Question : afficher la question
                libelle = item.texte || item.question || 'Cliquez ici';
            } else {
                // Réponse : afficher le contenu (data-contenu)
                libelle = item.contenu || 'Réponse';
            }
            if (libelle.length > 60) libelle = libelle.substring(0, 60) + '…';

            // Seule la question a l'icône 💡
            const icone = isQuestion ? '💡 ' : '';

            html += `<span class="trigger-element" data-type="${dataType}" data-contenu="${contenuAttr}" data-style="${styleAttr}" data-question="${questionAttr}"${bonneAttr}${isQuestionAttr}${styleAttribs}>${icone}${libelle}<span class="trigger-badge">🔗</span></span> `;
        });

        // #8 : mode QCM persistant dans l'attribut data-qcm
        const modeQCMAttr = modeQCM ? ' data-qcm="true"' : '';
        return `<span class="trigger-group"${modeQCMAttr}>${html}</span>`;
    },

    // ============================================================
    // SAUVEGARDER LES DÉCLENCHEURS DANS L'ÉDITEUR
    // ============================================================
    sauvegarder: function(editeur, listeDeclencheurs, modeQCM, elementOrigine, savedRange) {
        if (listeDeclencheurs.length === 0) {
            alert('⚠️ Aucun déclencheur à sauvegarder.');
            return false;
        }

        const groupeHTML = this.genererGroupe(listeDeclencheurs, modeQCM);

        if (elementOrigine && elementOrigine.parentNode) {
            const parent = elementOrigine.parentNode;
            const temp = document.createElement('div');
            temp.innerHTML = groupeHTML;
            const nouveauGroupe = temp.firstElementChild;

            if (parent.classList.contains('trigger-group')) {
                parent.parentNode.replaceChild(nouveauGroupe, parent);
            } else {
                const ancienGroupe = elementOrigine.closest('.trigger-group');
                if (ancienGroupe) {
                    ancienGroupe.parentNode.replaceChild(nouveauGroupe, ancienGroupe);
                }
            }
        } else if (savedRange) {
            const selection = window.getSelection();
            selection.removeAllRanges();
            selection.addRange(savedRange);
            document.execCommand('insertHTML', false, groupeHTML);
        } else {
            const range = document.createRange();
            range.selectNodeContents(editeur);
            range.collapse(false);
            const selection = window.getSelection();
            selection.removeAllRanges();
            selection.addRange(range);
            document.execCommand('insertHTML', false, groupeHTML);
        }

        // Ajouter la classe trigger-editor au nouveau groupe s'il est dans l'éditeur
        const editeurContainer = editeur.closest('.trigger-editor');
        if (editeurContainer) {
            editeurContainer.querySelectorAll('.trigger-group:not(.trigger-editor)').forEach(function(group) {
                group.classList.add('trigger-editor');
            });
        }

        return true;
    },

    // ============================================================
    // APPLIQUER LES STYLES AUX DÉCLENCHEURS
    // ============================================================
    appliquerStyles: function(container) {
        container.querySelectorAll('.trigger-element').forEach(el => {
            const tStyle = {
                color: el.dataset.tColor || '',
                font: el.dataset.tFont || '',
                size: el.dataset.tSize || '',
                bold: el.dataset.tBold === 'true',
                italic: el.dataset.tItalic === 'true',
                underline: el.dataset.tUnderline === 'true'
            };
            if (tStyle.color) el.style.color = tStyle.color;
            if (tStyle.font) el.style.fontFamily = tStyle.font;
            if (tStyle.size) el.style.fontSize = tStyle.size + 'px';
            if (tStyle.bold) el.style.fontWeight = 'bold';
            if (tStyle.italic) el.style.fontStyle = 'italic';
            if (tStyle.underline) {
                el.style.textDecoration = 'underline';
                el.style.textDecorationColor = tStyle.color || '#6f42c1';
            } else if (tStyle.color) {
                el.style.textDecoration = 'none';
            }
        });
    },

    // ============================================================
    // RÉVÉLER LES RÉPONSES (avec data-type)
    // ============================================================
    revelerReponses: function(container) {
        const groupe = container.querySelector('.trigger-group:not([data-qcm="true"])');
        if (!groupe) return 0;
        
        groupe.classList.add('reponses-visible');
        const elements = groupe.querySelectorAll('.trigger-element[data-type="reponse"]');
        return elements.length;
    },

    // ============================================================
    // MASQUER LES RÉPONSES
    // ============================================================
    masquerReponses: function(container) {
        const groupe = container.querySelector('.trigger-group:not([data-qcm="true"])');
        if (groupe) {
            groupe.classList.remove('reponses-visible');
        }
    },

    // ============================================================
    // RÉINITIALISER LES RÉPONSES
    // ============================================================
    reinitialiserReponses: function(container) {
        const groupes = container.querySelectorAll('.trigger-group:not([data-qcm="true"])');
        groupes.forEach(groupe => {
            groupe.classList.remove('reponses-visible');
        });
    },

    // ============================================================
    // APPLIQUER LE CORRIGÉ (QCM)
    // ============================================================
    appliquerCorrige: function(declencheurs, actif) {
        declencheurs.forEach(item => {
            if (actif) {
                if (item.bonne) {
                    item.element.classList.add('qcm-correct');
                    item.element.classList.remove('qcm-incorrect');
                } else {
                    item.element.classList.add('qcm-incorrect');
                    item.element.classList.remove('qcm-correct');
                }
            } else {
                item.element.classList.remove('qcm-correct', 'qcm-incorrect');
            }
        });
    },

    // ============================================================
    // DÉTECTER SI UN GROUPE EST EN MODE QCM
    // ============================================================
    estModeQCM: function(container) {
        const groupe = container.querySelector('.trigger-group');
        return groupe && groupe.dataset.qcm === 'true';
    },

    // ============================================================
    // #7 : COMPTER LES RÉPONSES (avec data-type)
    // ============================================================
    compterReponses: function(container) {
        const elements = container.querySelectorAll('.trigger-element[data-type="reponse"]');
        return elements.length;
    },

    // ============================================================
    // ATTACHER LES ÉVÉNEMENTS DE CLIC
    // ============================================================
    attacherEvenements: function(container, callbacks) {
        const defaults = {
            onPopup: function(titre, contenu) {
                alert(titre + '\n\n' + contenu);
            },
            onInline: function(element, contenu) {
                element.innerHTML = contenu;
            },
            onBottom: function(element, contenu) {
                var existing = element.parentNode.querySelector('.trigger-response');
                if (existing) existing.remove();
                var div = document.createElement('div');
                div.className = 'trigger-response';
                div.innerHTML = contenu;
                element.parentNode.insertBefore(div, element.nextSibling);
            }
        };

        const cbs = { ...defaults, ...callbacks };

        container.querySelectorAll('.trigger-element').forEach(el => {
            el.addEventListener('click', function(e) {
                e.stopPropagation();
                const contenu = this.dataset.contenu || '';
                const style = this.dataset.style || 'popup';
                const titre = this.dataset.question || this.textContent.replace(/[💡🔗📋✅❌]/g, '').trim();

                if (style === 'popup') {
                    cbs.onPopup(titre, contenu);
                } else if (style === 'inline') {
                    cbs.onInline(this, contenu);
                } else if (style === 'bottom') {
                    cbs.onBottom(this, contenu);
                }
            });
        });
    }
};

// Export pour Node.js (si besoin)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Triggers;
}