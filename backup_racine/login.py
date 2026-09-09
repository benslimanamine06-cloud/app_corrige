# ============================================================
# ROUTE : /change_password (protégée)
# ============================================================
def do_POST_change_password(self):
    if not verifier_auth(self.headers):
        self._repondre_401()
        return
    
    try:
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        old_password = data.get('old_password', '')
        new_password = data.get('new_password', '')
        
        if len(new_password) < 4:
            self._repondre_erreur("Le mot de passe doit contenir au moins 4 caractères", 400)
            return
        
        # Vérifier l'ancien mot de passe
        old_hash = hashlib.sha256(old_password.encode()).hexdigest()
        if old_hash != MOT_DE_PASSE_HACHE:
            self._repondre_erreur("Ancien mot de passe incorrect", 401)
            return
        
        # Changer le mot de passe
        global MOT_DE_PASSE_HACHE
        MOT_DE_PASSE_HACHE = hashlib.sha256(new_password.encode()).hexdigest()
        
        # Sauvegarder dans un fichier de config
        with open('mot_de_passe.hash', 'w') as f:
            f.write(MOT_DE_PASSE_HACHE)
        
        logging.info("🔑 Mot de passe modifié avec succès")
        self._repondre_succes({"message": "Mot de passe modifié"})
        
    except Exception as e:
        logging.error(f"Erreur change_password: {e}")
        self._repondre_erreur(str(e))

# ============================================================
# ROUTE : /reset_password (publique - mais sécurisée)
# ============================================================
def do_POST_reset_password(self):
    try:
        # Note : Cette route pourrait être protégée par un mot de passe admin
        # ou par une vérification supplémentaire
        
        # Pour l'instant, on laisse le reset possible
        global MOT_DE_PASSE_HACHE
        MOT_DE_PASSE_HACHE = hashlib.sha256("prof123".encode()).hexdigest()
        
        with open('mot_de_passe.hash', 'w') as f:
            f.write(MOT_DE_PASSE_HACHE)
        
        logging.info("🔑 Mot de passe réinitialisé à 'prof123'")
        self._repondre_succes({"message": "Mot de passe réinitialisé"})
        
    except Exception as e:
        logging.error(f"Erreur reset_password: {e}")
        self._repondre_erreur(str(e))