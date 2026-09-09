import os
import sys
import platform
import time
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess

class InstallerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Installation - Gestion de Classe")
        self.root.geometry("500x420")
        self.root.resizable(False, False)
        
        # En-tête
        ttk.Label(root, text="Assistant d'Installation", font=("Arial", 14, "bold")).pack(pady=15)
        ttk.Label(root, text="Plateforme Pédagogique - Gestion de Classe", font=("Arial", 10)).pack(pady=0)
        
        ttk.Separator(root, orient='horizontal').pack(fill='x', padx=20, pady=10)
        
        # ============================================================
        # SECTION : SYSTÈME D'EXPLOITATION
        # ============================================================
        ttk.Label(root, text="1. Choisissez votre système d'exploitation :", font=("Arial", 10, "bold")).pack(anchor="w", padx=30, pady=(10,5))
        
        self.os_var = tk.StringVar(value="linux")
        if platform.system() == "Windows":
            self.os_var.set("windows")
            
        ttk.Radiobutton(root, text="🐧 Linux (Ubuntu / Debian / autres)", variable=self.os_var, value="linux").pack(anchor="w", padx=50, pady=3)
        ttk.Radiobutton(root, text="🪟 Windows", variable=self.os_var, value="windows").pack(anchor="w", padx=50, pady=3)
        ttk.Radiobutton(root, text="🍎 macOS (expérimental)", variable=self.os_var, value="macos").pack(anchor="w", padx=50, pady=3)
        
        # ============================================================
        # SECTION : OPTIONS
        # ============================================================
        ttk.Label(root, text="2. Options :", font=("Arial", 10, "bold")).pack(anchor="w", padx=30, pady=(15,5))
        
        self.create_shortcut_var = tk.IntVar(value=1)
        ttk.Checkbutton(root, text="✅ Créer un raccourci sur le bureau", variable=self.create_shortcut_var).pack(anchor="w", padx=50, pady=2)
        
        self.check_deps_var = tk.IntVar(value=1)
        ttk.Checkbutton(root, text="🔍 Vérifier les dépendances (Python, PyQt5)", variable=self.check_deps_var).pack(anchor="w", padx=50, pady=2)
        
        ttk.Separator(root, orient='horizontal').pack(fill='x', padx=20, pady=10)
        
        # ============================================================
        # SECTION : PROGRESS & STATUS
        # ============================================================
        self.progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10)
        
        self.status_label = ttk.Label(root, text="🔹 Prêt pour l'installation", font=("Arial", 9))
        self.status_label.pack(pady=5)
        
        # ============================================================
        # SECTION : BOUTONS
        # ============================================================
        btn_frame = ttk.Frame(root)
        btn_frame.pack(pady=10)
        
        self.btn_install = ttk.Button(btn_frame, text="🚀 Installer", command=self.lancer_installation, width=15)
        self.btn_install.pack(side=tk.LEFT, padx=5)
        
        self.btn_quit = ttk.Button(btn_frame, text="❌ Quitter", command=self.root.quit, width=15)
        self.btn_quit.pack(side=tk.LEFT, padx=5)

    # ============================================================
    # FONCTIONS UTILITAIRES
    # ============================================================
    def get_desktop_path(self, choix_os):
        home = os.path.expanduser("~")
        if choix_os == "linux":
            for d in ["Bureau", "Desktop", "桌面", "Escritorio"]:
                path = os.path.join(home, d)
                if os.path.exists(path):
                    return path
            return os.path.join(home, "Bureau")
        elif choix_os == "macos":
            return os.path.join(home, "Desktop")
        else:
            return os.path.join(home, "Desktop")

    # ============================================================
    # #10 : VÉRIFICATION DES DÉPENDANCES
    # ============================================================
    def verifier_dependances(self):
        """Vérifie les dépendances nécessaires"""
        resultats = []
        
        # Vérifier Python
        try:
            python_version = subprocess.check_output(["python3", "--version"], stderr=subprocess.STDOUT, text=True)
            resultats.append(f"✅ Python : {python_version.strip()}")
        except:
            resultats.append("❌ Python 3 non trouvé")
            
        # Vérifier PyQt5
        try:
            subprocess.check_output(["python3", "-c", "import PyQt5"], stderr=subprocess.STDOUT, text=True)
            resultats.append("✅ PyQt5 : installé")
        except:
            resultats.append("⚠️ PyQt5 : non installé (l'application fonctionnera dans le navigateur)")
            
        # Vérifier PyQtWebEngine
        try:
            subprocess.check_output(["python3", "-c", "import PyQt5.QtWebEngineWidgets"], stderr=subprocess.STDOUT, text=True)
            resultats.append("✅ PyQtWebEngine : installé")
        except:
            resultats.append("⚠️ PyQtWebEngine : non installé (fonctionnalité de navigateur limitée)")
            
        return resultats

    # ============================================================
    # #9 : CRÉATION DES RACCOURCIS
    # ============================================================
    def creer_raccourci_linux(self, desktop_dir, app_py_path, script_dir):
        """Crée un raccourci .desktop robuste pour Linux"""
        desktop_file = os.path.join(desktop_dir, "GestionClasse.desktop")
        
        # #9 : .desktop avec bash -c pour éviter la dépendance à gnome-terminal
        contenu = f"""[Desktop Entry]
Name=Gestion de Classe
Comment=Plateforme Pédagogique
Exec=bash -c "cd '{script_dir}' && python3 app.py"
Terminal=true
Type=Application
Categories=Education;
Icon=applications-education
StartupNotify=true
"""
        with open(desktop_file, "w", encoding="utf-8") as f:
            f.write(contenu)
        os.chmod(desktop_file, 0o755)
        
        # Créer aussi un script .sh pour un lancement plus sûr
        sh_file = os.path.join(desktop_dir, "Lancer_GestionClasse.sh")
        sh_contenu = f"""#!/bin/bash
# Lanceur de la Plateforme Pédagogique
cd '{script_dir}'
python3 app.py
"""
        with open(sh_file, "w", encoding="utf-8") as f:
            f.write(sh_contenu)
        # #17 : Rendre le script exécutable
        os.chmod(sh_file, 0o755)
        
        return desktop_file, sh_file

    def creer_raccourci_windows(self, desktop_dir, app_py_path):
        """Crée un raccourci .bat pour Windows"""
        bat_file = os.path.join(desktop_dir, "GestionClasse.bat")
        contenu = f'''@echo off
echo ========================================
echo   📚 Gestion de Classe - Plateforme Pedagogique
echo ========================================
echo.
echo 📁 Dossier : {os.path.dirname(app_py_path)}
echo.
echo 🚀 Lancement du serveur...
echo.
echo    🌐 http://localhost:8000
echo    🔐 Mot de passe : prof123
echo.
echo    ⏹️  Pour arreter : Ctrl+C
echo.
echo ========================================
echo.
python "{app_py_path}"
pause
'''
        with open(bat_file, "w", encoding="utf-8") as f:
            f.write(contenu)
        return bat_file

    def creer_raccourci_macos(self, desktop_dir, app_py_path, script_dir):
        """Crée un script .command pour macOS"""
        command_file = os.path.join(desktop_dir, "Lancer_GestionClasse.command")
        contenu = f'''#!/bin/bash
# Lanceur de la Plateforme Pédagogique - macOS
cd "{script_dir}"
python3 app.py
'''
        with open(command_file, "w", encoding="utf-8") as f:
            f.write(contenu)
        os.chmod(command_file, 0o755)
        return command_file

    # ============================================================
    # INSTALLATION PRINCIPALE
    # ============================================================
    def lancer_installation(self):
        self.btn_install.config(state="disabled")
        self.btn_quit.config(state="disabled")
        self.status_label.config(text="⏳ Installation en cours...")
        self.root.update()
        
        # Simulation de progression
        for i in range(1, 31):
            self.progress["value"] = i
            self.root.update()
            time.sleep(0.01)
        
        dossier_actuel = os.path.dirname(os.path.abspath(__file__))
        app_py_path = os.path.join(dossier_actuel, "app.py")
        
        choix = self.os_var.get()
        desktop_dir = self.get_desktop_path(choix)
        
        try:
            # ============================================================
            # #10 : 1. VÉRIFICATION DES DÉPENDANCES
            # ============================================================
            if self.check_deps_var.get() == 1:
                self.status_label.config(text="🔍 Vérification des dépendances...")
                self.root.update()
                deps = self.verifier_dependances()
                
                # Afficher les résultats
                dep_msg = "Dépendances :\n" + "\n".join(deps)
                print(dep_msg)
                time.sleep(0.5)
            
            # Progression
            for i in range(31, 61):
                self.progress["value"] = i
                self.root.update()
                time.sleep(0.01)
            
            # ============================================================
            # #9 : 2. CRÉATION DES RACCOURCIS
            # ============================================================
            fichiers_crees = []
            
            if self.create_shortcut_var.get() == 1:
                self.status_label.config(text="📁 Création des raccourcis...")
                self.root.update()
                
                if choix == "linux":
                    fichiers = self.creer_raccourci_linux(desktop_dir, app_py_path, dossier_actuel)
                    fichiers_crees.extend(fichiers)
                elif choix == "macos":
                    fichiers = self.creer_raccourci_macos(desktop_dir, app_py_path, dossier_actuel)
                    fichiers_crees.append(fichiers)
                else:  # Windows
                    fichiers = self.creer_raccourci_windows(desktop_dir, app_py_path)
                    fichiers_crees.append(fichiers)
            
            # Progression
            for i in range(61, 91):
                self.progress["value"] = i
                self.root.update()
                time.sleep(0.01)
            
            # ============================================================
            # 3. FICHIER DE CONFIGURATION
            # ============================================================
            self.status_label.config(text="💾 Sauvegarde de la configuration...")
            self.root.update()
            
            config_file = os.path.join(dossier_actuel, "config.txt")
            with open(config_file, "w", encoding="utf-8") as f:
                f.write(f"install_path={dossier_actuel}\n")
                f.write(f"install_date={time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"os={choix}\n")
                f.write(f"python_version={sys.version.split()[0]}\n")
            fichiers_crees.append(config_file)
            
            # Progression finale
            for i in range(91, 101):
                self.progress["value"] = i
                self.root.update()
                time.sleep(0.01)
            
            # ============================================================
            # 4. MESSAGE DE FIN
            # ============================================================
            self.status_label.config(text="✅ Installation terminée avec succès !")
            self.root.update()
            
            # Construire le message
            msg = "✅ L'installation est réussie !\n\n"
            
            if self.create_shortcut_var.get() == 1:
                msg += "📁 Raccourcis créés sur le bureau :\n"
                for f in fichiers_crees:
                    msg += f"   • {os.path.basename(f)}\n"
                msg += "\n"
            
            msg += "🚀 Pour lancer l'application :\n"
            if choix == "linux":
                msg += "   • Double-cliquez sur 'Lancer_GestionClasse.sh'\n"
                msg += "   • Ou double-cliquez sur 'GestionClasse.desktop'\n"
            elif choix == "macos":
                msg += "   • Double-cliquez sur 'Lancer_GestionClasse.command'\n"
            else:
                msg += "   • Double-cliquez sur 'GestionClasse.bat'\n"
            
            msg += "\n🔐 Mot de passe par défaut : prof123"
            
            if self.check_deps_var.get() == 1:
                msg += "\n\n📋 Résultat des dépendances :\n" + "\n".join(deps)
            
            msg += "\n\nSouhaitez-vous fermer l'assistant ?"
            
            reponse = messagebox.askyesno("Installation Terminée", msg)
            if reponse:
                self.root.quit()
            else:
                self.btn_install.config(state="normal")
                self.btn_quit.config(state="normal")
                self.progress["value"] = 0
                self.status_label.config(text="🔹 Prêt")
                
        except Exception as e:
            self.status_label.config(text=f"❌ Erreur : {str(e)[:50]}")
            messagebox.showerror("Erreur", f"Une erreur s'est produite :\n\n{str(e)}")
            self.btn_install.config(state="normal")
            self.btn_quit.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = InstallerApp(root)
    root.mainloop()