import time
import random
import questionary
import json
import os

FICHIER_SAVE = "sauvegarde.json"

joueur = {
    "nom": "",
    "age": "",
    "etape": 0,
    "inventaire": []
}




def ouvrir_menu():
    while True:
        choix = questionary.select(
            "╔══════ MENU ══════╗",
            choices=[
                "📦 Voir l'inventaire",
                "👤 Infos du personnage",
                "💾 Sauvegarder",
                "❌ Quitter le jeu",
                "▶  Continuer l'aventure"
            ]
        ).ask()

        if choix == "📦 Voir l'inventaire":
            if joueur["inventaire"]:
                print("\n📦 Inventaire :")
                for item in joueur["inventaire"]:
                    print(f"  - {item}")
            else:
                print("\n📦 Ton inventaire est vide.")
            time.sleep(2)

        elif choix == "👤 Infos du personnage":
            print(f"\n👤 Nom    : {joueur['nom']}")
            print(f"   Âge    : {joueur['age']} ans")
            print(f"   Étape  : {joueur['etape']}")
            time.sleep(2)

        elif choix == "💾 Sauvegarder":
            with open(FICHIER_SAVE, "w") as f:
                json.dump(joueur, f)
            print("\n[Partie sauvegardée !]")
            time.sleep(1)

        elif choix == "❌ Quitter le jeu":
            with open(FICHIER_SAVE, "w") as f:
                json.dump(joueur, f)
            print("\nPartie sauvegardée. À bientôt !")
            exit()

        elif choix == "▶  Continuer l'aventure":
            break  # On retourne au jeu


def select_avec_menu(message, choices):
    """
    Wrapper autour de questionary.select().
    Ajoute automatiquement l'option Menu et relance si le joueur l'ouvre.
    """
    while True:
        choix = questionary.select(
            message,
            choices=choices + ["📋 Menu"]
        ).ask()

        if choix == "📋 Menu":
            ouvrir_menu()
            # Après le menu, on re-pose la même question
        else:
            return choix


# ==========================================
# CHARGEMENT DE LA SAUVEGARDE
# ==========================================

if os.path.exists(FICHIER_SAVE):
    reprendre = questionary.confirm("Une sauvegarde a été trouvée. Veux-tu reprendre ta partie ?").ask()
    if reprendre:
        with open(FICHIER_SAVE, "r") as fichier:
            joueur = json.load(fichier)
        print(f"\n--- Content de te revoir, {joueur['nom']} ! ---")
        time.sleep(2)


# ==========================================
# ÉTAPE 0 : CRÉATION DU PERSONNAGE
# ==========================================

if joueur["etape"] == 0:
    print("Salut, pour commencer crée ton personnage")
    joueur["nom"] = questionary.text("Comment s'appelle-t-il ?").ask()
    joueur["age"] = questionary.text("Quel âge a-t-il ?").ask()

    time.sleep(2)
    print("-------------------------------------------------")
    print(" #CRÉATION DU PERSONNAGE# ")
    print("-------------------------------------------------")

    barre = ["----", "----------", "--------------------", "-----------------------------",
             "--------------------------------------", "----------------------------------------------------"]
    for etape_barre in barre:
        time.sleep(0.5)
        print(etape_barre)

    print("# PERSONNAGE CRÉÉ #")
    time.sleep(1)
    print(f"Ton personnage s'appelle {joueur['nom']} et a {joueur['age']} ans.")
    print(f"{joueur['nom']} peut maintenant partir à l'aventure !")

    joueur["etape"] = 1
    with open(FICHIER_SAVE, "w") as fichier:
        json.dump(joueur, fichier)
    print("[Partie sauvegardée automatiquement]")
    time.sleep(3)


# ==========================================
# ÉTAPE 1 : LE DÉBUT / LA CACHETTE
# ==========================================

if joueur["etape"] == 1:
    print("-------------------------------------------------")
    print(" #DÉBUT DU SCÉNARIO# ")
    print("-------------------------------------------------")

    for _ in range(30):
        print("-------------------------------------------------")

    time.sleep(3)
    print("Les terminaux informatiques grésillent, affichant des lignes de code d'erreur en boucle.")
    time.sleep(3)
    print("Un voyant rouge clignote au plafond, projetant des ombres saccadées sur les murs en métal, sur le mur est ecrit en noir : MDP:VIP.")
    time.sleep(3)
    print("Soudain tu entends un bruit, ils arrivent !!!")
    time.sleep(3)

    cachette1 = select_avec_menu(
        "Cherche un endroit pour te cacher !",
        [
            "Sous la table",
            "Dans l'armoire",
            "Ne pas se cacher"
        ]
    )

    if cachette1 == "Sous la table":
        print("D'un geste rapide tu te glisses sous la table.")
        time.sleep(1)
        print("D'ici, tu ne vois que leurs jambes.")
        time.sleep(2)
        print("Ils commencent à parler et remarquent quelque chose...")

        chance = random.randint(1, 5)

        if chance == 2:
            print("Une alarme retentit... Ils sortent en courant !")
        else:
            print("L'un d'eux fait tomber un stylo, il se baisse et....")
            print("# GAME OVER #")
            print("#############################################")
            print("Crédits :")
            print("Développement : Moi")
            print("Interface graphique : Il n'y en a pas")
            print("#############################################")
            exit()

    elif cachette1 == "Dans l'armoire":
        print("Tu cours vers l'armoire et la fermes.")
        time.sleep(1)
        print("Depuis ta cachette tu écoutes leur conversation...")
        time.sleep(1)
        print("- Où est-il ?!")
        time.sleep(1)
        print("- Le patron va nous tuer !!!")
        time.sleep(1)
        print("- Allons le retrouver !")
        time.sleep(1)
        print("Ils partent en fermant derrière eux la porte à clé.")
        time.sleep(1)

    elif cachette1 == "Ne pas se cacher":
        confirm = questionary.confirm("Sûr ?").ask()
        if confirm:
            print("Ils t'attrapent et t'emmènent avec eux.")
            print("# GAME OVER #")
            exit()
        else:
            print("Ok alors choisis ! Vite !!")
            time.sleep(2)
            print("Trop tard, ils t'ont vu !")
            print("# GAME OVER #")
            exit()

    joueur["etape"] = 2
    with open(FICHIER_SAVE, "w") as fichier:
        json.dump(joueur, fichier)
    print("\n[Point de contrôle atteint. Partie sauvegardée !]")
    time.sleep(2)


# ==========================================
# ÉTAPE 2 : LA FOUILLE
# ==========================================

if joueur["etape"] == 2:
    print("\nTu sors de ta cachette et commences à chercher un moyen de t'enfuir.")

    choix2 = select_avec_menu(
        "Où vas-tu chercher ?",
        [
            "Vers les ordinateurs",
            "Dans les tiroirs",
            "Tu enfonces la porte"
        ]
    )

    if choix2 == "Tu enfonces la porte":
        print("Tu prends de l'élan, cours et te heurtes violemment contre la porte en acier trempé.")
        time.sleep(2)
        print("Un gros BOOOOOMM retentit.")
        print("La porte ne s'ouvre pas...")
        time.sleep(2)
        print("Tu entends marcher dans le couloir.")
        print("Plus le temps de se cacher....!")
        time.sleep(2)
        print("La porte s'ouvre et un garde d'au moins 2 mètres te prend par la veste et t'emmène avec lui.")
        print("# GAME OVER #")
        exit()

    elif choix2 == "Dans les tiroirs":
        print("Tu fouilles dans cet étrange tiroir.")
        time.sleep(2)
        print("Au fond de celui-ci se trouve une sorte de carte...")
        time.sleep(2)
        print("Sur cette dernière est écrit: # ACCÈS LEVEL -1 #")
        time.sleep(2)
        print("Dans ce même tiroir tu trouves aussi un stylo et du papier.")
        time.sleep(2)
        joueur["inventaire"].append("Carte d'accès LVL-1")
        joueur["inventaire"].append("Stylo")
        joueur["inventaire"].append("Feuille de papier")
        with open(FICHIER_SAVE, "w") as f:
            json.dump(joueur, f)
        print("Grâce à la carte d'accès tu ouvres l'épaisse porte qui bouche l'unique sortie.")

    elif choix2 == "Vers les ordinateurs":
        print("Sur un des écrans tu vois écrit #PRINT ACCES CARD#")
        time.sleep(2)
        MDP = input("À côté du bouton est écrit #ENTREZ LE MOT DE PASSE# : ")
        if MDP == "VIP":
            joueur["inventaire"].append("Carte d'accès VIP")
            print("Pass VIP accordé.")
        elif MDP == "PREMIUM":
            joueur["inventaire"].append("Carte d'accès PREMIUM")
            print("Pass PREMIUM accordé.")
        else:
            print("Mot de passe incorrect.")

        time.sleep(2)
        print("Tu cliques et une carte sort d'une sorte d'imprimante.")
        time.sleep(2)
        print("Sur cette dernière est écrit: # ACCÈS LEVEL -1 #")
        time.sleep(2)
        print("Sur le bureau tu trouves aussi un petit prototype de robot déchargé et une clé USB.")
        time.sleep(2)
        joueur["inventaire"].append("Carte d'accès LVL-1")
        joueur["inventaire"].append("Petit prototype de robot(déchargé)")
        joueur["inventaire"].append("Clé USB")
        with open(FICHIER_SAVE, "w") as f:
            json.dump(joueur, f)
        print("Grâce à la carte d'accès tu ouvres l'épaisse porte qui bouche l'unique sortie.")

    joueur["etape"] = 3
    with open(FICHIER_SAVE, "w") as fichier:
        json.dump(joueur, fichier)
    print("\n[Point de contrôle atteint. Partie sauvegardée !]")
    time.sleep(2)


# ==========================================
# ÉTAPE 3 : LE COULOIR
# ==========================================

if joueur["etape"] == 3:
    print("\n--- CHAPITRE 2 : LE COULOIR ---")
    time.sleep(2)
    print(f"Inventaire actuel : {joueur['inventaire']}")
    time.sleep(5)
    print("Tu entres dans un grand et sombre couloir...")
    time.sleep(2)
    print("À gauche il y a une grande porte métallique et à droite un couloir avec 2 portes de chaque côté et 1 une sorte d'ascenseur au bout.")
    time.sleep(2)
    print("Vite ! Je les entends, ils arrivent !")

    c = 0
    while c < 50:
        choix3 = select_avec_menu(
            "Où vas-tu aller ?",
            [
                "Grande porte métallique",
                "Ascenseur",
                "Porte mystère 1",
                "Porte mystère 2",
                "Porte mystère 3",
                "Porte mystère 4",
            ]
        )

        if choix3 == "Grande porte métallique":
            print("C'est verrouillé...")
            time.sleep(3)
            c += 1

        elif choix3 == "Ascenseur":
            print("Tu passes la carte sur le lecteur et l'ascenseur t'emmène dans les tréfonds du labo.")
            time.sleep(3)
            c += 50

        elif choix3 == "Porte mystère 1":
            if "Robot chargé" in joueur["inventaire"]:
                print("Le robot désintègre la porte et tu trouves une carte de l'étage 0 du labo.")
                time.sleep(3)
                joueur["inventaire"].append("Carte étage 0")
            else:
                print("Il n'y a rien ici.")
            time.sleep(3)
            c += 1

        elif choix3 == "Porte mystère 2":
            print("Il n'y a rien ici...")
            time.sleep(3)
            c += 1

        elif choix3 == "Porte mystère 3":
            print("Il est écrit : VIP seulement.")
            if "Carte d'accès VIP" in joueur["inventaire"]:
                time.sleep(2)
                print("#ACCÈS VIP AUTORISÉ#")
                time.sleep(2)
                print("Tu entres et trouves une batterie !")
                time.sleep(2)
                joueur["inventaire"].append("Batterie")
                if "Petit prototype de robot(déchargé)" in joueur["inventaire"]:
                    print("Tu insères la batterie dans le petit robot...")
                    time.sleep(2)
                    joueur["inventaire"].remove("Petit prototype de robot(déchargé)")
                    joueur["inventaire"].remove("Batterie")
                    joueur["inventaire"].append("Robot chargé")
                    print(">> Le robot s'allume ! Tu as maintenant un robot à tes côtés.")
                    time.sleep(2)
                    nom_robot = input("Trouve-lui un nom : ")
                    time.sleep(2)
                    print(f"{nom_robot} adore son prénom !")
                else:
                    print("Il te manque quelque chose pour effectuer une action...")
            else:
                print("Tu n'as pas la carte d'accès VIP...")
            time.sleep(3)
            c += 1

        elif choix3 == "Porte mystère 4":
            print("Tu entres et trouves une loupe posée seule sur une table.")
            joueur["inventaire"].append("Loupe")
            time.sleep(3)
            c += 1

    joueur["etape"] = 4
    with open(FICHIER_SAVE, "w") as fichier:
        json.dump(joueur, fichier)
    print("\n[Point de contrôle atteint. Partie sauvegardée !]")
    time.sleep(2)


# ==========================================
# ÉTAPE 4 : ÉTAGE -1
# ==========================================

if joueur["etape"] == 4:
    print("\n--- CHAPITRE 3 : Etage -1 ---")
    time.sleep(2)
    print(f"Inventaire actuel : {joueur['inventaire']}")
    time.sleep(5)
    print("Après une longue minute en ascenseur tu arrives enfin au -1.")
    print("En arrivant tu trouves par terre une clé USB avec marqué #PROGRAMME DE DEFENCE LVL1#")
    print("Tu la prends.")
    joueur["inventaire"].append("Clé USB #PROGRAMME DE DEFENCE LVL1#")

    if "Robot chargé" in joueur["inventaire"]:
        choix4 = select_avec_menu(
            "Veux-tu la brancher sur ton robot ?",
            ["OUI", "NON"]
        )

        if choix4 == "OUI":
            joueur["inventaire"].remove("Robot chargé")
            joueur["inventaire"].remove("Clé USB #PROGRAMME DE DEFENCE LVL1#")
            print("Tu insères la clé dans ton robot.")
            time.sleep(2)
            joueur["inventaire"].append("Robot défensif LVL1")
            print("#MISE À JOUR TERMINÉE#")
            time.sleep(2)
            print("Tu continues ton chemin.")

        elif choix4 == "NON":
            print("Tu continues ton chemin.")

    print("\n##SUITE DU JEU EN COURS DE DÉVELOPPEMENT##")
    print("")
    print("  ##EX DÉVELOPPEMENTS##")