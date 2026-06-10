import json
import time
import random
import questionary
import os

FICHIER_SAVE = "sauvegarde.json"

# ==========================================
# CHARGEMENT D'UNE SALLE
# ==========================================

def charger_salle(nom_salle):
    # Ouvre le fichier JSON de la salle demandée
    # ex: "cachette" → ouvre "salles/cachette.json"
    with open(f"salles/{nom_salle}.json") as f:
        return json.load(f)

# ==========================================
# AFFICHAGE DE LA DESCRIPTION
# ==========================================

def afficher_salle(salle):
    # Affiche chaque phrase de la description une par une
    for ligne in salle["description"]:
        print(ligne)
        time.sleep(2)

# ==========================================
# FONCTIONS INVENTAIRE
# ==========================================

def ajouter_item(nom, quantite=1):
    inv = joueur["inventaire"]
    inv[nom] = inv.get(nom, 0) + quantite
    print(f" [+{quantite} {nom} ajouté(s)]")

def retirer_item(nom, quantite=1):
    inv = joueur["inventaire"]
    if inv.get(nom, 0) >= quantite:
        inv[nom] -= quantite
        if inv[nom] == 0:
            del inv[nom]  # supprime l'entrée si quantité = 0
        return True
    print(f" [Pas assez de {nom}]")
    return False

def a_item(nom, quantite=1):
    return joueur["inventaire"].get(nom, 0) >= quantite

# ==========================================
# MENU
# ==========================================

def ouvrir_menu():
    while True:
        choix = questionary.select(
            "╔══════ MENU ══════╗",
            choices=[
                "📦 Voir l'inventaire",
                "💤 Infos du personnage",
                "🏪 Boutique",
                "🔴 Mises a jours",
                "💾 Sauvegarder",
                "❌ Quitter le jeu",
                "▶ Continuer l'aventure"
            ]
        ).ask()

        if choix == "📦 Voir l'inventaire":
            if joueur["inventaire"]:
                print("\n📦 Inventaire :")
                for nom, qte in joueur["inventaire"].items():
                    print(f" - {nom} x{qte}")
            else:
                print("\n📦 Ton inventaire est vide.")
            time.sleep(2)

        elif choix == "💤 Infos du personnage":
            print(f"\n💤 Nom : {joueur['nom']}")
            print(f"   Âge : {joueur['age']} ans")
            print(f"   Salle : {joueur['salle_actuelle']}")
            time.sleep(2)

        elif choix == "🏪 Boutique":
            choix_boutique = questionary.select(
                "╔══════🏪Boutique🏪══════╗",
                choices=[
                    "Pistolet(55 OR)",
                    "Batterie(70 OR)",
                    "1 Boulon(1 OR)",
                    "Regarder une pub pour 10 OR"
                ]
            ).ask()

            if choix_boutique == "Pistolet(55 OR)":
                if retirer_item("Or", 55):
                    ajouter_item("Pistolet")
                    print("Transaction reussie")
                    print("[-55 OR]")

            elif choix_boutique == "Batterie(70 OR)":
                if retirer_item("Or", 70):
                    ajouter_item("Batterie")
                    print("Transaction reussie")
                    print("[-70 OR]")

            elif choix_boutique == "1 Boulon(1 OR)":
                if retirer_item("Or", 1):
                    ajouter_item("Boulon", 1)
                    print("Transaction reussie")
                    print("[-1 OR]")

            elif choix_boutique == "Regarder une pub pour 10 OR":
                for i in [30, 25, 20, 15, 10, 5, 0]:
                    print(f"Pub[{i}]")
                    time.sleep(5)
                print("[Objet accordé]")
                ajouter_item("Or", 10)

            time.sleep(2)

        elif choix == "🔴 Mises a jours":
            print("╔══════🔴Mises a Jours Récentes🔴══════╗")
            print("✅ Amelioration du menu(Boutique, onglets update..)")
            print("⚙️  Etape 4 en cours(6/5/26)")
            print("⚙️  Etape 5 a venir(9/6/26)")
            time.sleep(3)

        elif choix == "💾 Sauvegarder":
            with open(FICHIER_SAVE, "w") as f:
                json.dump(joueur, f)
            print("[Partie sauvegardée !]")
            time.sleep(1)

        elif choix == "❌ Quitter le jeu":
            with open(FICHIER_SAVE, "w") as f:
                json.dump(joueur, f)
            print("Partie sauvegardée. À bientôt !")
            exit()

        elif choix == "▶ Continuer l'aventure":
            break

# ==========================================
# EXÉCUTION D'UN EFFET
# ==========================================

def executer_effet(effet, joueur):
    # Affiche un message
    if effet["type"] == "message":
        print(effet["texte"])
        time.sleep(1.5)

    # Ajoute un objet à l'inventaire
    elif effet["type"] == "ajouter_item":
        ajouter_item(effet["item"], effet.get("quantite", 1))

    # Retire un objet de l'inventaire
    elif effet["type"] == "retirer_item":
        retirer_item(effet["item"], effet.get("quantite", 1))

    # Change la salle actuelle du joueur
    elif effet["type"] == "aller_a":
        joueur["salle_actuelle"] = effet["salle"]

    # Fin du jeu
    elif effet["type"] == "game_over":
        print(effet["texte"])
        print("# GAME OVER #")
        exit()

    # Effet aléatoire : succes ou echec selon probabilité
    elif effet["type"] == "chance":
        succes = random.random() < effet["probabilite"]
        effets_a_jouer = effet["succes"] if succes else effet["echec"]
        for e in effets_a_jouer:
            executer_effet(e, joueur)

# ==========================================
# JOUER UNE SALLE
# ==========================================

def jouer_salle(salle, joueur):
    # Affiche la description de la salle
    afficher_salle(salle)

    # Récupère les textes des boutons depuis le JSON
    labels = [c["label"] for c in salle["choix"]]

    # Affiche les choix + le bouton Menu
    reponse = questionary.select("Que fais-tu ?", choices=labels + ["📋 Menu"]).ask()

    # Si le joueur ouvre le menu, on le lance puis on relance la même salle
    if reponse == "📋 Menu":
        ouvrir_menu()
        jouer_salle(salle, joueur)
        return

    # Trouve le choix sélectionné et exécute ses effets
    for choix in salle["choix"]:
        if choix["label"] == reponse:
            for effet in choix["effets"]:
                executer_effet(effet, joueur)

# ==========================================
# CHARGEMENT SAUVEGARDE OU CRÉATION JOUEUR
# ==========================================

joueur = {
    "nom": "",
    "age": "",
    "inventaire": {},
    "salle_actuelle": "cachette"
}

if os.path.exists(FICHIER_SAVE):
    reprendre = questionary.confirm("Une sauvegarde a été trouvée. Veux-tu reprendre ta partie ?").ask()
    if reprendre:
        with open(FICHIER_SAVE, "r") as f:
            joueur = json.load(f)
        print(f"\n--- Content de te revoir, {joueur['nom']} ! ---")
        time.sleep(2)

if joueur["nom"] == "":
    print("-------------------------------------------------")
    print("         #CRÉATION DU PERSONNAGE#               ")
    print("-------------------------------------------------")
    joueur["nom"] = questionary.text("Comment s'appelle ton personnage ?").ask()
    joueur["age"] = questionary.text("Quel âge a-t-il ?").ask()

    barre = ["----", "----------", "--------------------", "-----------------------------",
             "--------------------------------------", "----------------------------------------------------"]
    for etape_barre in barre:
        time.sleep(0.5)
        print(etape_barre)

    print("# PERSONNAGE CRÉÉ #")
    time.sleep(1)
    ajouter_item("Or", 100)
    print(f"Ton personnage s'appelle {joueur['nom']} et a {joueur['age']} ans.")
    print(f"{joueur['nom']} peut maintenant partir à l'aventure !")
    time.sleep(2)

# ==========================================
# BOUCLE PRINCIPALE
# ==========================================

while True:
    # Charge le fichier JSON de la salle actuelle
    salle = charger_salle(joueur["salle_actuelle"])
    # Lance la salle
    jouer_salle(salle, joueur)