import os
import time
import tkinter as tk
from tkinter import ttk, messagebox
import shutil

class UninstallerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Désinstallation - Gestion de Classe")
        self.root.geometry("450x350")
        self.root.resizable(False, False)
        
        # En-tête
        ttk.Label(root, text="Assistant de Désinstallation", font=("Arial", 14, "bold")).pack(pady=15)
        ttk.Label(root, text="Plateforme Pédagogique - Gestion de Classe", font=("Arial", 10)).pack(pady=0)
        
        ttk.Separator(root, orient='horizontal').pack(fill='x', padx=20, pady=10)
        
        # ============================================================
        # SECTION : OPTIONS DE DÉSINSTALLATION
        # ============================================================
        ttk.Label(root, text="Options de désinstallation :", font=("Arial", 10, "bold")).pack(anchor="w", padx=30, pady=(10,5))
        
        self.delete_shortcuts_var = tk.IntVar(value=1)
        ttk.Checkbutton(root, text="🗑️ Supprimer les raccourcis du bureau", 
                       variable=self.delete_shortcuts_var).pack(anchor="w", padx=50, pady=2)
        
        self.delete_data_var = tk.IntVar(value=0)
        ttk.Checkbutton(root, text="📊 Supprimer les données (donnees.json, photos, etc.)", 
                       variable=self.delete_data_var).pack(anchor="w", padx=50, pady=2)
        
        self.delete_config_var = tk.IntVar(value=1)
        ttk.Checkbutton(root, text="⚙️ Supprimer le fichier de configuration (config.txt)", 
                       variable=self.delete_config_var).pack(anchor="w", padx=50, pady=2)
        
        ttk.Separator(root, orient='horizontal').pack(fill='x', padx=20, pady=10)
        
        # ============================================================
        # SECTION : PROGRESS & STATUS
        # ============================================================
        self.progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10)
        
        self.status_label = ttk.Label(root, text="🔹 Prêt pour la désinstallation", font=("Arial", 9))
        self.status_label.pack(pady=5)
        
        # ============================================================
        # SECTION : BOUTONS
        # ============================================================
        btn_frame = ttk.Frame(root)
        btn_frame.pack(pady=10)
        
        self.btn_uninstall = ttk.Button(btn_frame, text="🗑️ Désinstaller", command=self.lancer_desinstallation, width=15)
        self.btn_uninstall.pack(side=tk.LEFT, padx=5)
        
        self.btn_quit = ttk.Button(btn_frame, text="❌ Quitter", command=self.root.quit, width=15)
        self.btn_quit.pack(side=tk.LEFT, padx=5)

    # ============================================================
    # FONCTIONS DE DÉSINSTALLATION
    # ============================================================
    def lancer_desinstallation(self):
        # ============================================================
        # 1. CONFIRMATION
        # ============================================================
        if self.delete_data_var.get() == 1:
            msg = "⚠️ ATTENTION : Vous avez choisi de supprimer les données.\n\n"
            msg += "Cela supprimera définitivement :\n"
            msg += "• donnees.json (tous les élèves, notes, cours, etc.)\n"
            msg += "• photos/ (toutes les photos des élèves)\n\n"
            msg += "Êtes-vous sûr de vouloir continuer ?"
        else:
            msg = "Êtes-vous sûr de vouloir procéder à la désinstallation ?"
        
        confirmation = messagebox.askyesno("Confirmation", msg)
        if not confirmation:
            return
        
        # ============================================================
        # 2. DÉSINSTALLATION
        # ============================================================
        self.btn_uninstall.config(state="disabled")
        self.btn_quit.config(state="disabled")
        self.status_label.config(text="⏳ Désinstallation en cours...")
        self.root.update()
        
        for i in range(1, 31):
            self.progress["value"] = i
            self.root.update()
            time.sleep(0.01)
            
        home = os.path.expanduser("~")
        dossier_actuel = os.path.dirname(os.path.abspath(__file__))
        
        fichiers_supprimes = []
        fichiers_non_trouves = []
        erreurs = []
        
        # ============================================================
        # #9 : 3. SUPPRESSION DES RACCOURCIS
        # ============================================================
        if self.delete_shortcuts_var.get() == 1:
            self.status_label.config(text="🗑️ Suppression des raccourcis...")
            self.root.update()
            
            chemins_raccourcis = [
                # Linux
                os.path.join(home, "Bureau", "GestionClasse.desktop"),
                os.path.join(home, "Desktop", "GestionClasse.desktop"),
                os.path.join(home, "Bureau", "Lancer_GestionClasse.sh"),
                os.path.join(home, "Desktop", "Lancer_GestionClasse.sh"),
                # Windows
                os.path.join(home, "Bureau", "GestionClasse.bat"),
                os.path.join(home, "Desktop", "GestionClasse.bat"),
                # macOS
                os.path.join(home, "Desktop", "Lancer_GestionClasse.command"),
            ]
            
            for chemin in chemins_raccourcis:
                if os.path.exists(chemin):
                    try:
                        os.remove(chemin)
                        fichiers_supprimes.append(chemin)
                        print(f"🗑️ Supprimé : {chemin}")
                    except Exception as e:
                        erreurs.append(f"❌ Erreur sur {chemin} : {e}")
                else:
                    fichiers_non_trouves.append(chemin)
        
        for i in range(31, 51):
            self.progress["value"] = i
            self.root.update()
            time.sleep(0.01)
        
        # ============================================================
        # 4. SUPPRESSION DU FICHIER DE CONFIGURATION
        # ============================================================
        if self.delete_config_var.get() == 1:
            self.status_label.config(text="⚙️ Suppression de la configuration...")
            self.root.update()
            
            config_file = os.path.join(dossier_actuel, "config.txt")
            if os.path.exists(config_file):
                try:
                    os.remove(config_file)
                    fichiers_supprimes.append(config_file)
                    print(f"🗑️ Supprimé : {config_file}")
                except Exception as e:
                    erreurs.append(f"❌ Erreur sur {config_file} : {e}")
            else:
                fichiers_non_trouves.append(config_file)
        
        for i in range(51, 71):
            self.progress["value"] = i
            self.root.update()
            time.sleep(0.01)
        
        # ============================================================
        # 5. SUPPRESSION DES DONNÉES (si demandé)
        # ============================================================
        if self.delete_data_var.get() == 1:
            self.status_label.config(text="📊 Suppression des données...")
            self.root.update()
            
            # Supprimer donnees.json
            data_file = os.path.join(dossier_actuel, "donnees.json")
            if os.path.exists(data_file):
                try:
                    os.remove(data_file)
                    fichiers_supprimes.append(data_file)
                    print(f"🗑️ Supprimé : {data_file}")
                except Exception as e:
                    erreurs.append(f"❌ Erreur sur {data_file} : {e}")
            else:
                fichiers_non_trouves.append(data_file)
            
            # Supprimer le dossier photos
            photos_dir = os.path.join(dossier_actuel, "photos")
            if os.path.exists(photos_dir):
                try:
                    shutil.rmtree(photos_dir)
                    fichiers_supprimes.append(photos_dir)
                    print(f"🗑️ Supprimé : {photos_dir}")
                except Exception as e:
                    erreurs.append(f"❌ Erreur sur {photos_dir} : {e}")
            else:
                fichiers_non_trouves.append(photos_dir)
        
        for i in range(71, 91):
            self.progress["value"] = i
            self.root.update()
            time.sleep(0.01)
        
        # ============================================================
        # 6. RÉSULTAT
        # ============================================================
        self.status_label.config(text="✅ Désinstallation terminée !")
        self.root.update()
        
        for i in range(91, 101):
            self.progress["value"] = i
            self.root.update()
            time.sleep(0.01)
        
        # Construire le message
        msg = "✅ Désinstallation terminée !\n\n"
        
        if fichiers_supprimes:
            msg += "📁 Fichiers supprimés :\n"
            for f in fichiers_supprimes[:10]:  # Limiter l'affichage
                msg += f"   • {os.path.basename(f)}\n"
            if len(fichiers_supprimes) > 10:
                msg += f"   ... et {len(fichiers_supprimes) - 10} autre(s)\n"
            msg += "\n"
        
        if erreurs:
            msg += "⚠️ Erreurs rencontrées :\n"
            for e in erreurs:
                msg += f"   • {e}\n"
            msg += "\n"
        
        if not fichiers_supprimes and not erreurs:
            msg += "   Aucun fichier à supprimer trouvé.\n"
            msg += "   (L'application est peut-être déjà désinstallée.)\n\n"
        
        msg += "🔹 Vous pouvez maintenant supprimer manuellement le dossier de l'application si vous le souhaitez.\n\n"
        msg += "🔐 Pensez à sauvegarder vos données avant de supprimer le dossier."
        
        time.sleep(0.5)
        messagebox.showinfo("Désinstallation Terminée", msg)
        
        self.btn_uninstall.config(state="normal")
        self.btn_quit.config(state="normal")
        self.progress["value"] = 0
        self.status_label.config(text="🔹 Prêt")

if __name__ == "__main__":
    root = tk.Tk()
    app = UninstallerApp(root)
    root.mainloop()