import sys
import threading
import os
import json
import subprocess
import platform
import socket
import hashlib
import secrets
import shutil
import logging
import re
from datetime import datetime, timedelta
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import cgi
from html.parser import HTMLParser
from html import unescape
from urllib.parse import urlparse, parse_qs

# ============================================================
# CONFIGURATION
# ============================================================
PORT = 8000
DATA_FILE = "data/donnees.json"
BACKUP_DIR = "instance/backups"
MAX_BACKUPS = 30

# Hash du mot de passe par défaut (prof123)
# Charger depuis le fichier s'il existe
MOT_DE_PASSE_HACHE = None

def charger_mot_de_passe():
    global MOT_DE_PASSE_HACHE
    if os.path.exists('mot_de_passe.hash'):
        try:
            with open('mot_de_passe.hash', 'r') as f:
                MOT_DE_PASSE_HACHE = f.read().strip()
            logging.info("🔑 Mot de passe chargé depuis mot_de_passe.hash")
        except:
            MOT_DE_PASSE_HACHE = hashlib.sha256("prof123".encode()).hexdigest()
    else:
        MOT_DE_PASSE_HACHE = hashlib.sha256("prof123".encode()).hexdigest()
        with open('mot_de_passe.hash', 'w') as f:
            f.write(MOT_DE_PASSE_HACHE)
        logging.info("🔑 Mot de passe par défaut créé: prof123")

charger_mot_de_passe()

# ============================================================
# LOGGING
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('plateforme.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# ============================================================
# DONNÉES
# ============================================================
DONNEES = {}
verrou_donnees = threading.Lock()

# ============================================================
# EXTRACTEUR HTML POUR DÉCLENCHEURS (sécurisé)
# ============================================================
class TriggerExtractor(HTMLParser):
    """Extrait les déclencheurs du HTML de manière sécurisée"""
    
    def __init__(self):
        super().__init__()
        self.triggers = []
        self.current_tag = None
        self.current_data = {}
        self.in_trigger = False
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'span' and attrs_dict.get('class') == 'trigger-element':
            self.in_trigger = True
            self.current_data = {}
            # Extraire tous les attributs data-*
            for key, value in attrs_dict.items():
                if key.startswith('data-'):
                    self.current_data[key] = value
    
    def handle_data(self, data):
        if self.in_trigger and data.strip():
            self.current_data['text'] = data.strip()
    
    def handle_endtag(self, tag):
        if tag == 'span' and self.in_trigger:
            if self.current_data:
                self.triggers.append(self.current_data)
            self.in_trigger = False
            self.current_data = {}

def extraire_texte_lisible(contenu_html):
    """Extrait le texte lisible d'un contenu HTML en préservant la structure des déclencheurs."""
    if not contenu_html:
        return ""
    
    # D'abord, extraire les déclencheurs avec le parser HTML
    extracteur = TriggerExtractor()
    extracteur.feed(contenu_html)
    
    # Texte final
    resultats = []
    
    for trigger in extracteur.triggers:
        question = trigger.get('data-question', '').strip()
        contenu = trigger.get('data-contenu', '').strip()
        is_question = trigger.get('data-type') == 'question' or trigger.get('data-is-question') == 'true'
        
        if is_question:
            resultats.append(f"\n❓ {question}")
        else:
            resultats.append(f"   → {contenu}")
    
    # Nettoyer le reste du HTML
    texte = contenu_html
    
    # Supprimer les balises de déclencheurs déjà traitées
    texte = re.sub(r'<span class="trigger-group"[^>]*>.*?</span>', '', texte, flags=re.DOTALL)
    
    # Nettoyer le HTML restant
    texte = re.sub(r'<p[^>]*>', '\n', texte)
    texte = re.sub(r'</p>', '\n', texte)
    texte = re.sub(r'<li[^>]*>', '  • ', texte)
    texte = re.sub(r'</li>', '\n', texte)
    texte = re.sub(r'<ul[^>]*>', '\n', texte)
    texte = re.sub(r'</ul>', '', texte)
    texte = re.sub(r'<ol[^>]*>', '\n', texte)
    texte = re.sub(r'</ol>', '', texte)
    texte = re.sub(r'<br\s*/?>', '\n', texte)
    texte = re.sub(r'<[^>]+>', '', texte)
    texte = re.sub(r'[ \t]+', ' ', texte)
    texte = re.sub(r'\n\s*\n\s*\n', '\n\n', texte)
    texte = texte.strip()
    texte = unescape(texte)
    
    # Ajouter les déclencheurs extraits
    if resultats:
        if texte:
            texte += "\n\n" + "\n".join(resultats)
        else:
            texte = "\n".join(resultats)
    
    return texte

def extraire_titre_lecon(seance):
    return seance.get('titreLecon', '')

# ============================================================
# CHARGEMENT DES DONNÉES
# ============================================================
def charger_donnees_disque():
    global DONNEES
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                DONNEES = json.load(f)
            logging.info(f"✅ Données chargées depuis {DATA_FILE}")
        except Exception as e:
            logging.error(f"❌ Erreur de chargement: {e}")
            DONNEES = {}
    else:
        DONNEES = {}
        logging.info("ℹ️ Aucun fichier de données existant, création d'un nouveau")

# ============================================================
# SAUVEGARDE ATOMIQUE AVEC BACKUPS
# ============================================================
def sauvegarder_donnees(nouvelles_donnees):
    """Sauvegarde les données de manière atomique avec backup"""
    try:
        # 1. Créer le dossier de backups
        os.makedirs(BACKUP_DIR, exist_ok=True)
        
        # 2. Faire un backup si le fichier existe
        if os.path.exists(DATA_FILE):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(BACKUP_DIR, f"donnees_{timestamp}.json")
            shutil.copy2(DATA_FILE, backup_file)
            
            # Garder seulement les MAX_BACKUPS plus récents
            backups = sorted([
                f for f in os.listdir(BACKUP_DIR) 
                if f.startswith("donnees_") and f.endswith(".json")
            ])
            if len(backups) > MAX_BACKUPS:
                for f in backups[:-MAX_BACKUPS]:
                    os.remove(os.path.join(BACKUP_DIR, f))
                    logging.info(f"🗑️ Ancien backup supprimé: {f}")
        
        # 3. Écrire dans un fichier temporaire
        temp_file = DATA_FILE + ".tmp"
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(nouvelles_donnees, f, ensure_ascii=False, indent=4)
        
        # 4. Renommer atomiquement
        os.replace(temp_file, DATA_FILE)
        
        logging.info(f"✅ Données sauvegardées dans {DATA_FILE}")
        return True
        
    except Exception as e:
        logging.error(f"❌ Erreur de sauvegarde: {e}")
        return False

# ============================================================
# VALIDATION DES CHEMINS (sécurité)
# ============================================================
def valider_chemin(chemin, base_dir="."):
    """Vérifie que le chemin est dans le répertoire autorisé"""
    chemin_absolu = os.path.abspath(chemin)
    base_absolu = os.path.abspath(base_dir)
    if not chemin_absolu.startswith(base_absolu):
        raise ValueError(f"Chemin non autorisé: {chemin}")
    return chemin_absolu

# ============================================================
# SERVEUR HTTP
# ============================================================
class GestionnaireDonnees(SimpleHTTPRequestHandler):
    
    def _repondre_401(self):
        """Réponse non autorisée"""
        self.send_response(401)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({
            "status": "unauthorized", 
            "message": "Authentification requise"
        }).encode('utf-8'))
    
    def _repondre_403(self, message="Accès non autorisé"):
        """Réponse interdite"""
        self.send_response(403)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({
            "status": "forbidden", 
            "message": message
        }).encode('utf-8'))
    
    def _repondre_succes(self, data=None):
        """Réponse succès"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {"status": "success"}
        if data:
            response.update(data)
        self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def _repondre_erreur(self, message, code=500):
        """Réponse erreur"""
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({
            "status": "error", 
            "message": message
        }).encode('utf-8'))
    
    # ============================================================
    # ROUTE : /load (protégée - maintenant publique)
    # ============================================================
    def do_GET_load(self):
        # L'authentification a été supprimée
        with verrou_donnees:
            # Inclure les versions PAR CLÉ dans la réponse
            # (corrige le bug de "Conflit de version" permanent : un compteur
            # global était partagé par toutes les clés, donc la sauvegarde
            # d'une donnée quelconque invalidait la version de toutes les autres)
            response = dict(DONNEES)
            response['_versions'] = DONNEES.get('_versions', {})
            self._repondre_succes(response)
    
    # ============================================================
    # ROUTE : /photo (GET - maintenant publique)
    # ============================================================
    def do_GET_photo(self):
        # L'authentification a été supprimée
        try:
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            niveau = params.get('niveau', [''])[0]
            id_eleve = params.get('id', [''])[0]

            if not niveau or not id_eleve:
                self._repondre_erreur("Niveau et ID requis", 400)
                return

            chemin = os.path.join('photos', niveau, f"{id_eleve}.jpg")
            
            # Valider le chemin
            try:
                valider_chemin(chemin, "photos")
            except ValueError:
                self._repondre_403()
                return
            
            if not os.path.exists(chemin):
                self.send_response(404)
                self.end_headers()
                return

            with open(chemin, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-type', 'image/jpeg')
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            
        except Exception as e:
            logging.error(f"Erreur GET photo: {e}")
            self._repondre_erreur(str(e))
    
    # ============================================================
    # ROUTE : /save (protégée - maintenant publique)
    # ============================================================
    def do_POST_save(self):
        # L'authentification a été supprimée
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            new_data = json.loads(post_data.decode('utf-8'))

            # Identifier la clé métier envoyée (tout le payload sauf _version)
            cles = [k for k in new_data.keys() if k != '_version']
            if len(cles) != 1:
                self._repondre_erreur(
                    "Le payload doit contenir exactement une clé de données", 400
                )
                return
            cle = cles[0]

            with verrou_donnees:
                # Vérifier la version DE CETTE CLÉ UNIQUEMENT (conflit)
                versions = DONNEES.setdefault('_versions', {})
                version_client = new_data.get('_version', 0)
                version_serveur = versions.get(cle, 0)

                if version_client < version_serveur:
                    logging.warning(
                        f"⚠️ Conflit de version sur '{cle}': "
                        f"client={version_client}, serveur={version_serveur}"
                    )
                    self._repondre_succes({
                        "status": "conflict",
                        "version_serveur": version_serveur,
                        "message": f"Conflit de version détecté sur {cle}"
                    })
                    return

                # Mettre à jour uniquement la clé concernée
                DONNEES[cle] = new_data[cle]
                versions[cle] = version_serveur + 1

                # Sauvegarde atomique
                if sauvegarder_donnees(DONNEES):
                    # Export des séances en fichiers texte
                    self._exporter_seances_texte(new_data)
                    self._repondre_succes({
                        "version": versions[cle]
                    })
                else:
                    self._repondre_erreur("Erreur de sauvegarde", 500)

        except json.JSONDecodeError as e:
            logging.error(f"JSON invalide: {e}")
            self._repondre_erreur("Données JSON invalides", 400)
        except Exception as e:
            logging.error(f"Erreur save: {e}", exc_info=True)
            self._repondre_erreur(str(e))
    
    def _exporter_seances_texte(self, new_data):
        """Exporte les séances en fichiers texte"""
        try:
            for cle, seances in new_data.items():
                if cle.startswith("donnees_seances_"):
                    partie = cle.replace("donnees_seances_", "")
                    elements = partie.split('__')
                    if len(elements) >= 3:
                        niveau = elements[0].replace('_', ' ')
                        trimestre = elements[1].replace('_', ' ')
                        module = elements[2].replace('_', ' ')
                        dossier_module = os.path.join(niveau, trimestre, module)
                        os.makedirs(dossier_module, exist_ok=True)
                        
                        for idx, seance in enumerate(seances):
                            titre = seance.get("titre", f"seance_{idx}")
                            
                            contenu_parts = []
                            
                            titre_lecon = extraire_titre_lecon(seance)
                            if titre_lecon:
                                contenu_parts.append(f"📖 {titre_lecon}")
                                contenu_parts.append("=" * (len(titre_lecon) + 3))
                                contenu_parts.append("")
                            
                            contenu_brut = seance.get("contenu", "")
                            if contenu_brut:
                                contenu_texte = extraire_texte_lisible(contenu_brut)
                                if contenu_texte:
                                    contenu_parts.append(contenu_texte)
                            
                            diaporama = seance.get("diaporama", [])
                            if diaporama and len(diaporama) > 0:
                                contenu_parts.append("")
                                contenu_parts.append("--- DIAPORAMA ---")
                                for d_idx, diapo in enumerate(diaporama):
                                    contenu_diapo = diapo.get("contenu", "")
                                    if contenu_diapo:
                                        contenu_parts.append(f"\n[Diapositive {d_idx + 1}]")
                                        contenu_parts.append(extraire_texte_lisible(contenu_diapo))
                            
                            if len(contenu_parts) == 0:
                                contenu_parts.append("(Contenu vide)")
                            
                            contenu_final = "\n".join(contenu_parts)
                            contenu_final = re.sub(r'\n{3,}', '\n\n', contenu_final)
                            
                            nom_fichier = "".join(c for c in titre if c.isalnum() or c in (' ', '-', '_')).rstrip()
                            if not nom_fichier:
                                nom_fichier = f"seance_{idx}"
                            chemin_fichier = os.path.join(dossier_module, f"{nom_fichier}.txt")
                            
                            with open(chemin_fichier, 'w', encoding='utf-8') as f:
                                f.write(f"--- {titre} ---\n\n")
                                f.write(contenu_final)
        except Exception as e:
            logging.error(f"Erreur export texte: {e}")
    
    # ============================================================
    # ROUTE : /photo (POST - maintenant publique)
    # ============================================================
    def do_POST_photo(self):
        # L'authentification a été supprimée
        try:
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )
            niveau = form.getvalue('niveau')
            id_eleve = form.getvalue('id')
            fichier = form['photo']
            
            if not niveau or not id_eleve:
                self._repondre_erreur("Niveau et ID requis", 400)
                return

            dossier = os.path.join('photos', niveau)
            os.makedirs(dossier, exist_ok=True)
            chemin = os.path.join(dossier, f"{id_eleve}.jpg")
            
            # Valider le chemin
            try:
                valider_chemin(chemin, "photos")
            except ValueError:
                self._repondre_403()
                return

            with open(chemin, 'wb') as f:
                f.write(fichier.file.read())

            logging.info(f"📸 Photo importée: {chemin}")
            self._repondre_succes({"path": chemin})
            
        except Exception as e:
            logging.error(f"Erreur upload photo: {e}")
            self._repondre_erreur(str(e))
    
    # ============================================================
    # ROUTE : /photo (DELETE - maintenant publique)
    # ============================================================
    def do_DELETE_photo(self):
        # L'authentification a été supprimée
        try:
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            niveau = params.get('niveau', [''])[0]
            id_eleve = params.get('id', [''])[0]

            if not niveau or not id_eleve:
                self._repondre_erreur("Niveau et ID requis", 400)
                return

            chemin = os.path.join('photos', niveau, f"{id_eleve}.jpg")
            
            # Valider le chemin
            try:
                valider_chemin(chemin, "photos")
            except ValueError:
                self._repondre_403()
                return
            
            fichier_supprime = os.path.exists(chemin)
            if fichier_supprime:
                os.remove(chemin)
                logging.info(f"🗑️ Photo supprimée: {chemin}")

            # Mettre à jour le JSON (vider le champ photo)
            with verrou_donnees:
                if 'all_eleves' in DONNEES and 'donnees' in DONNEES['all_eleves']:
                    donnees_eleves = DONNEES['all_eleves']['donnees']
                    
                    if niveau in donnees_eleves:
                        eleves = donnees_eleves[niveau].get('eleves', [])
                        
                        try:
                            index = int(id_eleve)
                            if 0 <= index < len(eleves):
                                if eleves[index].get('photo'):
                                    eleves[index]['photo'] = ''
                                    logging.info(f"📸 Photo vidée pour l'élève {index} du niveau {niveau}")
                        except ValueError:
                            for eleve in eleves:
                                if eleve.get('photo') and chemin in eleve.get('photo', ''):
                                    eleve['photo'] = ''
                                    logging.info(f"📸 Photo vidée pour l'élève {eleve.get('nom', 'inconnu')}")
                                    break
                        
                        sauvegarder_donnees(DONNEES)

            self._repondre_succes({
                "message": "Photo supprimée",
                "fichier_supprime": fichier_supprime
            })
            
        except Exception as e:
            logging.error(f"Erreur DELETE photo: {e}")
            self._repondre_erreur(str(e))
    
    # ============================================================
    # ROUTE : /upload_fichier (maintenant publique)
    # ============================================================
    def do_POST_upload_fichier(self):
        # L'authentification a été supprimée
        try:
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )
            fichier = form['fichier']
            chemin = form.getvalue('chemin')
            
            # Valider le chemin
            try:
                chemin_valide = valider_chemin(chemin)
            except ValueError as e:
                self._repondre_403(str(e))
                return
            
            os.makedirs(chemin_valide, exist_ok=True)
            nom_fichier = fichier.filename
            chemin_fichier = os.path.join(chemin_valide, nom_fichier)
            
            with open(chemin_fichier, 'wb') as f:
                f.write(fichier.file.read())
            
            logging.info(f"📄 Fichier uploadé: {chemin_fichier}")
            self._repondre_succes()
            
        except Exception as e:
            logging.error(f"Erreur upload fichier: {e}")
            self._repondre_erreur(str(e))
    
    # ============================================================
    # ROUTE : /open_folder (maintenant publique)
    # ============================================================
    def do_POST_open_folder(self):
        # L'authentification a été supprimée
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            chemin = data.get('chemin', '')
            
            # Valider le chemin
            try:
                chemin_valide = valider_chemin(chemin)
            except ValueError as e:
                self._repondre_403(str(e))
                return
            
            os.makedirs(chemin_valide, exist_ok=True)
            
            systeme = platform.system()
            if systeme == 'Windows':
                os.startfile(chemin_valide)
            elif systeme == 'Darwin':
                subprocess.run(['open', chemin_valide])
            else:
                subprocess.run(['xdg-open', chemin_valide])
            
            logging.info(f"📂 Dossier ouvert: {chemin_valide}")
            self._repondre_succes()
            
        except Exception as e:
            logging.error(f"Erreur open_folder: {e}")
            self._repondre_erreur(str(e))
    
    # ============================================================
    # ROUTE : /favicon.ico
    # ============================================================
    def do_GET_favicon(self):
        self.send_response(204)
        self.end_headers()
    
    # ============================================================
    # DISPATCHER PRINCIPAL
    # ============================================================
    def do_GET(self):
        try:
            # Routes publiques
            if self.path == '/favicon.ico':
                self.do_GET_favicon()
                return
            
            if self.path == '/load':
                self.do_GET_load()
                return
            
            if self.path.startswith('/photo'):
                self.do_GET_photo()
                return
            
            # ============================================================
            # FICHIERS STATIQUES
            # ============================================================
            # On extrait le chemin sans la query string (?param=valeur)
            # pour vérifier correctement l'extension du fichier
            chemin_sans_query = urlparse(self.path).path
            
            # Fichiers statiques (autorisés sans auth)
            if chemin_sans_query.endswith(('.html', '.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico')):
                super().do_GET()
                return
            
            # Si le chemin correspond à un fichier existant, le servir
            # (permet de servir des fichiers sans extension ou avec d'autres extensions)
            if chemin_sans_query.startswith('/'):
                chemin_fichier = chemin_sans_query[1:]  # Enlever le / initial
            else:
                chemin_fichier = chemin_sans_query
            
            if os.path.exists(chemin_fichier) and not os.path.isdir(chemin_fichier):
                super().do_GET()
                return
            
            # Autres routes -> 404
            self.send_response(404)
            self.end_headers()
            
        except Exception as e:
            logging.error(f"Erreur GET: {e}", exc_info=True)
            self._repondre_erreur(str(e))
    
    def do_POST(self):
        try:
            # Routes publiques - les routes d'authentification ont été supprimées
            
            if self.path == '/save':
                self.do_POST_save()
                return
            
            if self.path == '/photo':
                self.do_POST_photo()
                return
            
            if self.path == '/upload_fichier':
                self.do_POST_upload_fichier()
                return
            
            if self.path == '/open_folder':
                self.do_POST_open_folder()
                return
            
            # Autres routes -> 404
            self.send_response(404)
            self.end_headers()
            
        except Exception as e:
            logging.error(f"Erreur POST: {e}", exc_info=True)
            self._repondre_erreur(str(e))
    
    def do_DELETE(self):
        try:
            if self.path.startswith('/photo'):
                self.do_DELETE_photo()
                return
            
            self.send_response(405)
            self.end_headers()
            
        except Exception as e:
            logging.error(f"Erreur DELETE: {e}", exc_info=True)
            self._repondre_erreur(str(e))
    
    def log_message(self, format, *args):
        # Désactiver les logs HTTP par défaut
        pass

# ============================================================
# LANCEMENT DU SERVEUR
# ============================================================
def run_server():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    charger_donnees_disque()
    httpd = ThreadingHTTPServer(('0.0.0.0', PORT), GestionnaireDonnees)

    print("\n" + "="*50)
    print("  📚 PLATEFORME PÉDAGOGIQUE - SERVEUR ACTIF")
    print("="*50)

    hostname = socket.gethostname()
    ip_local = socket.gethostbyname(hostname)

    print(f"\n  🔗 SUR L'ORDINATEUR :")
    print(f"     http://localhost:{PORT}")
    print(f"     http://{ip_local}:{PORT}")
    print(f"\n  📱 SUR LE SMARTPHONE :")
    print(f"     http://{ip_local}:{PORT}")
    print(f"\n  ⚠️  Les deux appareils doivent être sur le même réseau WiFi")
    print("\n" + "="*50)
    print("  ▶️  Appuyez sur Ctrl+C pour arrêter le serveur")
    print("="*50 + "\n")

    httpd.serve_forever()

# ============================================================
# APPLICATION PYQT5
# ============================================================
try:
    from PyQt5.QtWidgets import QApplication, QMainWindow
    from PyQt5.QtWebEngineWidgets import QWebEngineView
    from PyQt5.QtCore import QUrl
except ImportError:
    logging.warning("⚠️ PyQt5 non installé. Lancement du serveur seul...")
    threading.Thread(target=run_server, daemon=True).start()
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n⏹️ Serveur arrêté.")
        sys.exit(0)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestion de Classe")
        self.resize(1024, 768)
        self.browser = QWebEngineView()
        self.browser.page().profile().clearHttpCache()
        self.browser.setUrl(QUrl(f"http://localhost:{PORT}/index.html"))  # Changé de login.html à index.html
        self.setCentralWidget(self.browser)

def main():
    threading.Thread(target=run_server, daemon=True).start()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️ Application interrompue.")
        sys.exit(0)
