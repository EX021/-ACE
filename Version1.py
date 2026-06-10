import time
import random
import questionary
import json
import os

FICHIER_SAVE = "sauvegarde.json"

# ==========================================
# Catalogue des Items
# ==========================================

ITEMS_DATA = {
    "or": {
        "name": "Or",
        "type": "currency",
    },
    "pistolet": {
        "name": "Pistolet",
        "type": "weapon",
        "power": 100,
    },
    "Serigue explosive": {
        "name": "Seringue explosive",
        "type": "weapon",
        "power": 150,
    },
    "Canon a antimatière": {
        "name": "Canon à antimatière",
        "type": "weapon",
        "power": 10000000,
    },
    "Katana technologique": {
        "name": "Katana technologique",
        "type": "weapon",
        "power": 1000000000,
    },
    "batterie": {
        "name": "Batterie",
        "type": "consumable",
    },
    "kit_soin": {
        "name": "Kit de soin",
        "type": "consumable",
        "heal": 50,
    },
    "Seringue soignante": {
        "name": "Seringue soignante",
        "type": "consumable",
        "heal": 100,
    },
    "boulon": {
        "name": "Boulon",
        "type": "material",
    },
    "stylo": {
        "name": "Stylo",
        "type": "misc",
    },
    "feuille_papier": {
        "name": "Feuille de papier",
        "type": "misc",
    },
    "loupe": {
        "name": "Loupe",
        "type": "tool",
    },
    "cle_usb": {
        "name": "Clé USB",
        "type": "tool",
    },
    "cle_usb_defence_lvl1": {
        "name": "Clé USB #PROGRAMME DE DEFENCE LVL1#",
        "type": "tool",
    },
    "carte_acces_lvl1": {
        "name": "Carte d'accès LVL-1",
        "type": "keycard",
        "level": 1,
    },
    "carte_acces_lvl2": {
        "name": "Carte d'accès LVL-2",
        "type": "keycard",
        "level": 2,
    },
    "carte_acces_vip": {
        "name": "Carte d'accès VIP",
        "type": "keycard",
        "level": "vip",
    },
    "carte_acces_premium": {
        "name": "Carte d'accès PREMIUM",
        "type": "keycard",
        "level": "premium",
    },
    "carte_etage_0": {
        "name": "Carte étage 0",
        "type": "keycard",
        "level": 0,
    },
    "robot_decharge": {
        "name": "Petit prototype de robot (déchargé)",
        "type": "companion",
        "charged": False,
    },
    "robot_charge": {
        "name": "Robot chargé",
        "type": "companion",
        "charged": True,
    },
    "robot_defensif_lvl1": {
        "name": "Robot défensif LVL1",
        "type": "weapon",
        "charged": True,
        "power": 50,
    },
}

ENNEMIS_DATA = {
    "Sientifique": {
        "name": "Scientifique",
        "pv": 80,
        "degats": 8,
        "recompense_or": 10,
        "xp": 25,
    },
    "Garde_LVL-1": {
        "name": "Garde",
        "pv": 120,
        "degats": 15,
        "recompense_or": 50,
        "xp": 40,
    },
    "Boss_LVL-1": {
        "name": "Scientifique fou",
        "pv": 200,
        "degats": 22,
        "recompense_or": 200,
        "xp": 80,
    },
    "Horde de sientifiques": {
        "name": "Une horde de scientifiques",
        "pv": 600,
        "degats": 27,
        "recompense_or": 234,
        "xp": 345,
    },
}

AMELIORATIONS_DATA = {
    "pistolet": {
        "niveau_max": 100,
        "cout_or_par_niveau": 432,
        "bonus_power_par_niveau": 76,
    },
    "robot_defensif_lvl1": {
        "niveau_max": 100,
        "cout_or_par_niveau": 176,
        "bonus_power_par_niveau": 95,
    },
    "Katana technologique": {
        "niveau_max": 10000,
        "cout_or_par_niveau": 1000000000000,
        "bonus_power_par_niveau": 500000,
    },
    "Canon a antimatière": {
        "niveau_max": 1000,
        "cout_or_par_niveau": 1000000000,
        "bonus_power_par_niveau": 5000,
    },
}


def get_item_data(item_id):
    if item_id in ITEMS_DATA:
        return ITEMS_DATA[item_id]
    return {"name": item_id, "type": "misc"}


joueur = {
    "nom": "",
    "age": "",
    "etape": 0,
    "inventaire": {},
    "stats": {
        "ennemis_tues": 0,
        "or_total_gagne": 0,
        "morts": 0,
    },
    "niveau": 1,
    "xp": 0,
    "pv": 100,
    "pv_max": 100,
    "degats_base": 10,
}

dev_mode = False
MOT_DE_PASSE_DEV = "dev1234"


# ==========================================
# FONCTIONS INVENTAIRE
# ==========================================

def ajouter_item(item_id, quantite=1):
    inv = joueur["inventaire"]
    if item_id in inv:
        inv[item_id]["qty"] += quantite
    else:
        data = get_item_data(item_id).copy()
        data["qty"] = quantite
        inv[item_id] = data
    nom = get_item_data(item_id)["name"]
    print(f" [+{quantite} {nom} ajouté(s)]")


def retirer_item(item_id, quantite=1):
    inv = joueur["inventaire"]
    if inv.get(item_id, {}).get("qty", 0) >= quantite:
        inv[item_id]["qty"] -= quantite
        if inv[item_id]["qty"] == 0:
            del inv[item_id]
        return True
    nom = get_item_data(item_id)["name"]
    print(f" [Pas assez de {nom}]")
    return False


def a_item(item_id, quantite=1):
    return joueur["inventaire"].get(item_id, {}).get("qty", 0) >= quantite


def get_qty(item_id):
    return joueur["inventaire"].get(item_id, {}).get("qty", 0)


# ==========================================
# FONCTIONS XP / NIVEAU
# ==========================================

def xp_requis(niveau):
    return niveau * 100


def gagner_xp(quantite):
    joueur["xp"] += quantite
    print(f" [+{quantite} XP]")
    while joueur["xp"] >= xp_requis(joueur["niveau"]):
        joueur["xp"] -= xp_requis(joueur["niveau"])
        joueur["niveau"] += 1
        joueur["pv_max"] += 25
        joueur["pv"] = joueur["pv_max"]
        joueur["degats_base"] += 5
        print(f"✨ NIVEAU {joueur['niveau']} atteint !")
        print(f"   PV max : {joueur['pv_max']}  |  Dégâts de base : {joueur['degats_base']}")
        print(f"   ❤️  PV entièrement restaurés !")


def afficher_barre_xp():
    niveau = joueur["niveau"]
    xp = joueur["xp"]
    requis = xp_requis(niveau)
    rempli = int((xp / requis) * 20)
    barre = "█" * rempli + "░" * (20 - rempli)
    print(f"  ⭐ Niveau {niveau}  [{barre}] {xp}/{requis} XP")


# ==========================================
# FONCTIONS COMBAT TOUR PAR TOUR
# ==========================================

def afficher_barres_combat(pv_ennemi, pv_ennemi_max, nom_ennemi):
    ratio_j = max(0, joueur["pv"] / joueur["pv_max"])
    rempli_j = int(ratio_j * 15)
    barre_j = "█" * rempli_j + "░" * (15 - rempli_j)

    ratio_e = max(0, pv_ennemi / pv_ennemi_max)
    rempli_e = int(ratio_e * 15)
    barre_e = "█" * rempli_e + "░" * (15 - rempli_e)

    print(f"\n  👤 {joueur['nom']:<10} [{barre_j}] {joueur['pv']}/{joueur['pv_max']} PV")
    print(f"  💀 {nom_ennemi[:10]:<10} [{barre_e}] {pv_ennemi}/{pv_ennemi_max} PV")
    print()


def choisir_arme_combat():
    weapons = [
        iid for iid, it in joueur["inventaire"].items()
        if it.get("type") == "weapon" and it.get("qty", 0) > 0
    ]
    if not weapons:
        return None, joueur["degats_base"], "mains nues"

    choix = questionary.select(
        "⚔️ Choisis une arme :",
        choices=[
            questionary.Choice(
                title=f"{joueur['inventaire'][w]['name']} (puissance: {joueur['inventaire'][w].get('power', '?')})",
                value=w
            )
            for w in weapons
        ] + [questionary.Choice(title="👊 Mains nues", value=None)]
    ).ask()

    if choix is None or choix not in joueur["inventaire"]:
        return None, joueur["degats_base"], "mains nues"
    return choix, joueur["inventaire"][choix].get("power", joueur["degats_base"]), joueur["inventaire"][choix]["name"]


def choisir_soin_combat():
    consommables = [
        iid for iid, it in joueur["inventaire"].items()
        if it.get("type") == "consumable" and it.get("heal") and it.get("qty", 0) > 0
    ]
    if not consommables:
        print("  Aucun consommable de soin dans l'inventaire !")
        time.sleep(1)
        return False

    choix = questionary.select(
        "💊 Quel item utiliser ?",
        choices=[
            questionary.Choice(
                title=f"{joueur['inventaire'][c]['name']} (+{joueur['inventaire'][c]['heal']} PV) x{joueur['inventaire'][c]['qty']}",
                value=c
            )
            for c in consommables
        ] + [questionary.Choice(title="❌ Annuler", value=None)]
    ).ask()

    if choix is None:
        return False

    soin = joueur["inventaire"][choix]["heal"]
    retirer_item(choix)
    avant = joueur["pv"]
    joueur["pv"] = min(joueur["pv_max"], joueur["pv"] + soin)
    print(f"  💊 Tu utilises {get_item_data(choix)['name']} : +{joueur['pv'] - avant} PV !")
    time.sleep(0.8)
    return True


def game_over():
    print("\n# GAME OVER #")
    print("#############################################")
    print("Crédits :")
    print("Développement : Moi")
    print("Interface graphique : Il n'y en a pas (pour l'instant)")
    print("#############################################")
    exit()


def combat(ennemi_id):
    ennemi_base = ENNEMIS_DATA[ennemi_id]
    pv_ennemi = ennemi_base["pv"]
    pv_ennemi_max = ennemi_base["pv"]
    nom = ennemi_base["name"]
    degats_ennemi = ennemi_base["degats"]

    print(f"\n╔══ ⚔️  COMBAT — {nom} ══╗")
    time.sleep(1)

    arme_id, degats_joueur, nom_arme = choisir_arme_combat()
    print(f"\n  Arme choisie : {nom_arme} ({degats_joueur} dégâts de base)")
    time.sleep(1)

    tour = 1

    while joueur["pv"] > 0 and pv_ennemi > 0:
        print(f"\n─── Tour {tour} ───")
        afficher_barres_combat(pv_ennemi, pv_ennemi_max, nom)

        action = questionary.select(
            "Que fais-tu ?",
            choices=[
                questionary.Choice(title=f"⚔️  Attaquer  ({degats_joueur} dégâts)", value="attaquer"),
                questionary.Choice(title="🛡️  Défendre  (réduit les dégâts reçus de 50%)", value="defendre"),
                questionary.Choice(title="💊 Utiliser un item de soin", value="soin"),
                questionary.Choice(title="🔄 Changer d'arme", value="changer_arme"),
            ]
        ).ask()

        if action == "attaquer":
            variation = random.uniform(0.9, 1.1)
            degats_tour = max(1, int(degats_joueur * variation))
            pv_ennemi -= degats_tour
            print(f"  ⚔️  Tu frappes {nom} pour {degats_tour} dégâts !")
            time.sleep(0.6)

        elif action == "defendre":
            print("  🛡️  Tu te mets en position défensive...")
            time.sleep(0.6)

        elif action == "soin":
            choisir_soin_combat()
            time.sleep(0.3)

        elif action == "changer_arme":
            arme_id, degats_joueur, nom_arme = choisir_arme_combat()
            print(f"  🔄 Arme changée : {nom_arme} ({degats_joueur} dégâts)")
            time.sleep(0.6)

        if pv_ennemi > 0:
            if action == "defendre":
                degats_recus = max(1, int(degats_ennemi * 0.5))
                print(f"  💥 {nom} attaque, mais ta défense réduit les dégâts : -{degats_recus} PV !")
            else:
                variation_e = random.uniform(0.85, 1.15)
                degats_recus = max(1, int(degats_ennemi * variation_e))
                print(f"  💥 {nom} contre-attaque : -{degats_recus} PV !")
            joueur["pv"] -= degats_recus
            joueur["pv"] = max(0, joueur["pv"])
            time.sleep(0.8)

        tour += 1

    if pv_ennemi <= 0:
        print(f"\n✅ {nom} est vaincu en {tour - 1} tours !")
        time.sleep(1)
        joueur["stats"]["ennemis_tues"] += 1

        recompense = ennemi_base.get("recompense_or", 0)
        if recompense:
            ajouter_item("or", recompense)
            joueur["stats"]["or_total_gagne"] += recompense
            print(f"  Tu gagnes {recompense} OR !")
            time.sleep(1)

        gagner_xp(ennemi_base.get("xp", 20))
        return True  # victoire

    else:
        joueur["stats"]["morts"] += 1
        print(f"\n❌ Tu es vaincu par {nom}...")
        time.sleep(1)
        game_over()
        return False  # défaite


# ==========================================
# FONCTIONS AMELIORATION
# ==========================================

def get_ameliorables():
    ameliorables = []
    for item_id in AMELIORATIONS_DATA:
        if item_id in joueur["inventaire"]:
            item = joueur["inventaire"][item_id]
            niveau = item.get("niveau", 1)
            niveau_max = AMELIORATIONS_DATA[item_id]["niveau_max"]
            ameliorables.append(
                questionary.Choice(
                    title=f"{item['name']} (niv. {niveau}/{niveau_max})",
                    value=item_id
                )
            )
    return ameliorables


def ameliorer_item(item_id):
    item = joueur["inventaire"].get(item_id)
    config = AMELIORATIONS_DATA[item_id]
    niveau_actuel = item.get("niveau", 1)
    niveau_max = config["niveau_max"]

    if niveau_actuel >= niveau_max:
        print(f"Niveau maximum atteint ({niveau_max}) !")
        return

    cout = config["cout_or_par_niveau"] * niveau_actuel
    bonus = config["bonus_power_par_niveau"]

    print(f"\n⬆️ {item['name']} — Niveau {niveau_actuel} → {niveau_actuel + 1}")
    print(f"   Coût : {cout} OR  |  Bonus power : +{bonus}")

    if not questionary.confirm("Améliorer ?").ask():
        return

    if not a_item("or", cout):
        print(f"Pas assez d'or ! (il faut {cout} OR)")
        return

    retirer_item("or", cout)
    item["niveau"] = niveau_actuel + 1
    item["power"] = item.get("power", 0) + bonus
    print(f"✅ {item['name']} amélioré ! Power : {item['power']}")


# ==========================================
# SAUVEGARDE
# ==========================================

def sauvegarder():
    with open(FICHIER_SAVE, "w") as f:
        json.dump(joueur, f)
    print("[Partie sauvegardée !]")


# ==========================================
# MENU
# ==========================================

def ouvrir_menu():
    global dev_mode
    while True:
        label_dev = "🛠️ Mode Dev [ACTIF]" if dev_mode else "🛠️ Mode Dev"
        choix = questionary.select(
            "╔══════ MENU ══════╗",
            choices=[
                "📦 Voir l'inventaire",
                "👤 Infos du personnage",
                "📊 Statistiques",
                "🪙 Boutique",
                "⬆️ Améliorer un item",
                "🔴 Mises a jours",
                "🔒 Codes",
                label_dev,
                "💾 Sauvegarder",
                "❌ Quitter le jeu",
                "▶ Continuer l'aventure"
            ]
        ).ask()

        if choix == "📦 Voir l'inventaire":
            if joueur["inventaire"]:
                print("\n📦 Inventaire :")
                for item_id, item in joueur["inventaire"].items():
                    nom   = item.get("name", item_id)
                    type_ = item.get("type", "?")
                    qty   = item.get("qty", 0)
                    extras = {k: v for k, v in item.items() if k not in ("name", "type", "qty")}
                    extra_str = "  " + "  ".join(f"{k}:{v}" for k, v in extras.items()) if extras else ""
                    print(f"  - [{type_}] {nom} x{qty}{extra_str}")
            else:
                print("\n📦 Ton inventaire est vide.")
            time.sleep(2)

        elif choix == "👤 Infos du personnage":
            print(f"\n👤 Nom    : {joueur['nom']}")
            print(f"   Âge   : {joueur['age']} ans")
            print(f"   Étape : {joueur['etape']}")
            print(f"   ❤️   PV : {joueur['pv']}/{joueur['pv_max']}")
            print(f"   ⚔️   Dégâts de base : {joueur['degats_base']}")
            afficher_barre_xp()
            time.sleep(2)

        elif choix == "📊 Statistiques":
            s = joueur["stats"]
            print("\n╔══════ 📊 STATISTIQUES ══════╗")
            print(f"  🗡️  Ennemis tués    : {s['ennemis_tues']}")
            print(f"  🪙  Or total gagné  : {s['or_total_gagne']}")
            print(f"  💀  Morts           : {s['morts']}")
            print(f"  📍  Étape actuelle  : {joueur['etape']}")
            print(f"  📦  Items possédés  : {sum(i['qty'] for i in joueur['inventaire'].values())}")
            time.sleep(3)

        elif choix == "🔒 Codes":
            CODE = input("Entrez un code promotionnel : ")
            if CODE == "PLUS ULTRA":
                ajouter_item("or", 10 ** 140)
                print("Recompense accordée !")
            elif CODE == "LEGO":
                ajouter_item("Katana technologique")
                print("Recompense accordée !")
            elif CODE == "MEDIC":
                ajouter_item("kit_soin", 5)
                print("Recompense accordée !")
            else:
                print("Code incorrect")

        elif choix == "⬆️ Améliorer un item":
            ameliorables = get_ameliorables()
            if not ameliorables:
                print("Tu n'as aucun item améliorable.")
            else:
                item_choisi = questionary.select(
                    "Quel item améliorer ?",
                    choices=ameliorables + [questionary.Choice(title="❌ Annuler", value=None)]
                ).ask()
                if item_choisi:
                    ameliorer_item(item_choisi)

        elif choix == "🪙 Boutique":
            choix_boutique = questionary.select(
                "╔══════🪙Boutique🪙══════╗",
                choices=[
                    "Pistolet (55 OR)",
                    "Kit de soin (30 OR)",
                    "Batterie (70 OR)",
                    "1 Boulon (1 OR)",
                    "Canon a antimatière (1 000 000 000 OR)",
                    "Regarder une pub pour 10 OR"
                ]
            ).ask()

            or_actuel = get_qty("or")

            if choix_boutique == "Pistolet (55 OR)":
                if or_actuel >= 55:
                    retirer_item("or", 55)
                    ajouter_item("pistolet")
                    print("Transaction reussie  [-55 OR]")
                else:
                    print(f"Pas assez d'or ! (tu as {or_actuel} OR, il en faut 55)")

            elif choix_boutique == "Kit de soin (30 OR)":
                if or_actuel >= 30:
                    retirer_item("or", 30)
                    ajouter_item("kit_soin")
                    print("Transaction reussie  [-30 OR]")
                else:
                    print(f"Pas assez d'or ! (tu as {or_actuel} OR, il en faut 30)")

            elif choix_boutique == "Batterie (70 OR)":
                if or_actuel >= 70:
                    retirer_item("or", 70)
                    ajouter_item("batterie")
                    print("Transaction reussie  [-70 OR]")
                else:
                    print(f"Pas assez d'or ! (tu as {or_actuel} OR, il en faut 70)")

            elif choix_boutique == "1 Boulon (1 OR)":
                if or_actuel >= 1:
                    retirer_item("or", 1)
                    ajouter_item("boulon")
                    print("Transaction reussie  [-1 OR]")
                else:
                    print("Pas assez d'or !")

            elif choix_boutique == "Canon a antimatière (1 000 000 000 OR)":
                if or_actuel >= 1000000000:
                    retirer_item("or", 1000000000)
                    ajouter_item("Canon a antimatière")
                    print("Transaction reussie  [-1 000 000 000 OR]")
                else:
                    print(f"Pas assez d'or ! (tu as {or_actuel} OR, il en faut 1 000 000 000)")

            elif choix_boutique == "Regarder une pub pour 10 OR":
                for i in range(30, -1, -5):
                    print(f"Pub[{i}]")
                    time.sleep(5)
                print("[Objet accordé]")
                ajouter_item("or", 10)

        elif choix == "🔴 Mises a jours":
            print("╔══════🔴Mises a Jours Récentes🔴══════╗")
            print("✅-Amelioration du menu (Boutique, onglet update..)")
            print("✅-Inventaire type JSON (name, type, qty)")
            print("✅-Système de combat tour par tour")
            print("✅-Système d'amélioration d'items")
            print("✅-Système de statistiques")
            print("✅-Système XP / Niveau / PV persistants")
            print("✅-Soins en combat et en boutique")
            print("✅-Etape 4")
            print("✅-Mode Dev")
            print("✅-Correction des bugs de progression d'étapes")
            print("⚙️-Etape 5 (en cours)")
            print("==========Détails==========")
            print("-Actions disponibles en combat :")
            print("  Attaquer / Défendre / Soin / Changer d'arme")
            print("-Ameliorations disponibles :")
            print("  Pistolet, Robot de défense, Canon, Katana")
            time.sleep(3)

        elif choix == label_dev:
            if not dev_mode:
                mdp = input("🔑 Mot de passe dev : ")
                if mdp == MOT_DE_PASSE_DEV:
                    dev_mode = True
                    print("✅ Mode développeur activé !")
                else:
                    print("❌ Mot de passe incorrect.")
                time.sleep(1)
            else:
                choix_dev = questionary.select(
                    "🛠️ ═══ OUTILS DEV ═══",
                    choices=[
                        "🔢 Changer d'étape",
                        "📦 Ajouter un item",
                        "💰 Ajouter de l'or",
                        "❤️  Remplir les PV",
                        "⭐ Ajouter de l'XP",
                        "💀 God Mode (PV infinis)",
                        "🔴 Désactiver le mode dev",
                        "↩️  Retour"
                    ]
                ).ask()

                if choix_dev == "🔢 Changer d'étape":
                    etape = input(f"Étape actuelle : {joueur['etape']}. Nouvelle étape : ")
                    try:
                        joueur["etape"] = int(etape)
                        print(f"✅ Étape changée à {joueur['etape']}")
                    except ValueError:
                        print("❌ Valeur invalide.")
                    time.sleep(1)

                elif choix_dev == "📦 Ajouter un item":
                    print("Items disponibles :")
                    for i, item_id in enumerate(ITEMS_DATA):
                        print(f"  {i:>2}. {item_id}")
                    item_id = input("ID de l'item : ").strip()
                    if item_id in ITEMS_DATA:
                        qty = input("Quantité (défaut 1) : ").strip()
                        qty = int(qty) if qty.isdigit() else 1
                        ajouter_item(item_id, qty)
                    else:
                        print("❌ Item inconnu.")
                    time.sleep(1)

                elif choix_dev == "💰 Ajouter de l'or":
                    montant = input("Montant d'or à ajouter : ").strip()
                    try:
                        ajouter_item("or", int(montant))
                    except ValueError:
                        print("❌ Valeur invalide.")
                    time.sleep(1)

                elif choix_dev == "❤️  Remplir les PV":
                    joueur["pv"] = joueur["pv_max"]
                    print(f"✅ PV restaurés à {joueur['pv_max']}")
                    time.sleep(1)

                elif choix_dev == "⭐ Ajouter de l'XP":
                    xp = input("XP à ajouter : ").strip()
                    try:
                        gagner_xp(int(xp))
                    except ValueError:
                        print("❌ Valeur invalide.")
                    time.sleep(1)

                elif choix_dev == "💀 God Mode (PV infinis)":
                    joueur["pv_max"] = 999999
                    joueur["pv"] = 999999
                    joueur["degats_base"] = 999999
                    print("☠️  GOD MODE activé ! PV et dégâts mis à 999 999.")
                    time.sleep(1)

                elif choix_dev == "🔴 Désactiver le mode dev":
                    dev_mode = False
                    print("🔴 Mode dev désactivé.")
                    time.sleep(1)

        elif choix == "💾 Sauvegarder":
            sauvegarder()
            time.sleep(1)

        elif choix == "❌ Quitter le jeu":
            sauvegarder()
            print("À bientôt !")
            exit()

        elif choix == "▶ Continuer l'aventure":
            break


def select_avec_menu(message, choices):
    while True:
        choix = questionary.select(
            message,
            choices=choices + ["📋 Menu"]
        ).ask()
        if choix == "📋 Menu":
            ouvrir_menu()
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

        joueur.setdefault("stats", {"ennemis_tues": 0, "or_total_gagne": 0, "morts": 0})
        joueur.setdefault("niveau", 1)
        joueur.setdefault("xp", 0)
        joueur.setdefault("pv", 100)
        joueur.setdefault("pv_max", 100)
        joueur.setdefault("degats_base", 10)
        joueur.pop("donjon_etage_max", None)

        if isinstance(joueur["inventaire"], list):
            ancien = joueur["inventaire"]
            joueur["inventaire"] = {}
            for item_name in ancien:
                if item_name:
                    item_id = next(
                        (k for k, v in ITEMS_DATA.items() if v["name"] == item_name),
                        item_name.lower().replace(" ", "_")
                    )
                    if item_id in joueur["inventaire"]:
                        joueur["inventaire"][item_id]["qty"] += 1
                    else:
                        data = get_item_data(item_id).copy()
                        data["qty"] = 1
                        joueur["inventaire"][item_id] = data

        elif isinstance(joueur["inventaire"], dict):
            for item_id, val in list(joueur["inventaire"].items()):
                if isinstance(val, (int, float)):
                    data = get_item_data(item_id).copy()
                    data["qty"] = int(val)
                    joueur["inventaire"][item_id] = data

        print(f"\n--- Content de te revoir, {joueur['nom']} ! ---")
        time.sleep(2)


# ==========================================
# BOUCLE PRINCIPALE DU JEU
# ==========================================
# CORRECTIF MAJEUR : les étapes étaient toutes des "if" indépendants,
# ce qui faisait s'enchaîner toutes les étapes au lancement.
# Maintenant chaque étape est dans une fonction, et la boucle principale
# gère la progression proprement.

def etape_0():
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
    print("Bravo tu as créé ton personnage, tu gagnes 100 or et 2 kits de soin !")
    ajouter_item("or", 100)
    ajouter_item("kit_soin", 2)
    print(f"Ton personnage s'appelle {joueur['nom']} et a {joueur['age']} ans.")
    print(f"{joueur['nom']} peut maintenant partir à l'aventure !")

    joueur["etape"] = 1
    sauvegarder()
    time.sleep(3)


def etape_1():
    print("-------------------------------------------------")
    print(" #DÉBUT DU SCÉNARIO# ")
    print("-------------------------------------------------")

    for _ in range(30):
        print("-------------------------------------------------")

    time.sleep(3)
    print("Les terminaux informatiques grésillent, affichant des lignes de code d'erreur en boucle.")
    time.sleep(3)
    print("Un voyant rouge clignote au plafond, projetant des ombres saccadées sur les murs en métal.")
    time.sleep(2)
    print("Sur le mur est écrit en noir : MDP:VIP.")
    time.sleep(3)
    print("Soudain tu entends un bruit, ils arrivent !!!")
    time.sleep(3)

    cachette1 = select_avec_menu(
        "Cherche un endroit pour te cacher !",
        ["Sous la table", "Dans l'armoire", "Ne pas se cacher"]
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
            print("L'un d'eux fait tomber un stylo, il se baisse et te voit !")
            time.sleep(1)
            print("Il t'attaque !")
            combat("Garde_LVL-1")
            print("Tu mets le garde KO et tu restes caché.")

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
            game_over()
        else:
            print("Ok alors choisis ! Vite !!")
            time.sleep(2)
            print("Trop tard, ils t'ont vu !")
            game_over()

    joueur["etape"] = 2
    sauvegarder()
    print("\n[Point de contrôle atteint. Partie sauvegardée !]")
    time.sleep(2)


def etape_2():
    print("\nTu sors de ta cachette et commences à chercher un moyen de t'enfuir.")

    choix2 = select_avec_menu(
        "Où vas-tu chercher ?",
        ["Vers les ordinateurs", "Dans les tiroirs", "Tu enfonces la porte"]
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
        print("La porte s'ouvre et un garde d'au moins 2 mètres te prend par la veste.")
        time.sleep(1)
        print("Il t'attaque !")
        time.sleep(1)
        combat("Garde_LVL-1")
        print("Tu mets le garde KO et tu récupères sa carte d'accès !")
        ajouter_item("carte_acces_lvl1")

    elif choix2 == "Dans les tiroirs":
        print("Tu fouilles dans cet étrange tiroir.")
        time.sleep(2)
        print("Au fond de celui-ci se trouve une sorte de carte...")
        time.sleep(2)
        print("Sur cette dernière est écrit: # ACCÈS LEVEL -1 #")
        time.sleep(2)
        print("Dans ce même tiroir tu trouves aussi un stylo et du papier.")
        time.sleep(2)
        ajouter_item("carte_acces_lvl1")
        ajouter_item("stylo")
        ajouter_item("feuille_papier")
        print("Grâce à la carte d'accès tu ouvres l'épaisse porte qui bouche l'unique sortie.")

    elif choix2 == "Vers les ordinateurs":
        print("Sur un des écrans tu vois écrit #PRINT ACCES CARD#")
        time.sleep(2)
        MDP = input("À côté du bouton est écrit #ENTREZ LE MOT DE PASSE# : ")
        if MDP == "VIP":
            ajouter_item("carte_acces_vip")
            print("Pass VIP accordé.")
        elif MDP == "PREMIUM":
            ajouter_item("carte_acces_premium")
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
        ajouter_item("carte_acces_lvl1")
        ajouter_item("robot_decharge")
        ajouter_item("cle_usb")
        print("Grâce à la carte d'accès tu ouvres l'épaisse porte qui bouche l'unique sortie.")

    joueur["etape"] = 3
    sauvegarder()
    print("\n[Point de contrôle atteint. Partie sauvegardée !]")
    time.sleep(2)


def etape_3():
    print("\n--- CHAPITRE 2 : LE COULOIR ---")
    time.sleep(2)
    print("À gauche il y a une grande porte métallique et à droite un couloir avec 2 portes de chaque côté et un ascenseur au bout.")
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
            time.sleep(2)
            print("Un garde surgit de derrière la porte !")
            time.sleep(1)
            combat("Garde_LVL-1")
            print("Le garde est à terre. La porte reste verrouillée...")
            time.sleep(2)
            c += 1

        elif choix3 == "Ascenseur":
            print("Tu passes la carte sur le lecteur et l'ascenseur t'emmène dans les tréfonds du labo.")
            time.sleep(3)
            c += 50

        elif choix3 == "Porte mystère 1":
            if a_item("robot_charge"):
                print("Le robot désintègre la porte et tu trouves une carte de l'étage 0 du labo.")
                time.sleep(3)
                ajouter_item("carte_etage_0")
            else:
                print("Il n'y a rien ici.")
            time.sleep(2)
            c += 1

        elif choix3 == "Porte mystère 2":
            print("Un scientifique t'attendait derrière cette porte !")
            time.sleep(1)
            combat("Sientifique")
            print("La salle est vide sinon. Tu repars.")
            time.sleep(2)
            c += 1

        elif choix3 == "Porte mystère 3":
            print("Il est écrit : VIP seulement.")
            if a_item("carte_acces_vip"):
                time.sleep(2)
                print("#ACCÈS VIP AUTORISÉ#")
                time.sleep(2)
                print("Tu entres et trouves une batterie et un kit de soin !")
                time.sleep(2)
                ajouter_item("batterie")
                ajouter_item("kit_soin")
                if a_item("robot_decharge"):
                    print("Tu insères la batterie dans le petit robot...")
                    time.sleep(2)
                    retirer_item("robot_decharge")
                    retirer_item("batterie")
                    ajouter_item("robot_charge")
                    print(">> Le robot s'allume ! Tu as maintenant un robot à tes côtés.")
                    time.sleep(2)
                    nom_robot = input("Trouve-lui un nom : ")
                    time.sleep(2)
                    print(f"{nom_robot} adore son prénom !")
            else:
                print("Tu n'as pas la carte d'accès VIP...")
            time.sleep(2)
            c += 1

        elif choix3 == "Porte mystère 4":
            print("Tu entres et trouves une loupe et un kit de soin posés sur une table.")
            ajouter_item("loupe")
            ajouter_item("kit_soin")
            time.sleep(2)
            c += 1

    joueur["etape"] = 4
    sauvegarder()
    print("\n[Point de contrôle atteint. Partie sauvegardée !]")
    time.sleep(2)


def etape_4():
    print("\n--- CHAPITRE 3 : Étage -1 ---")
    time.sleep(2)
    print("Après une longue minute en ascenseur tu arrives enfin au -1.")
    print("En arrivant tu trouves par terre une clé USB avec marqué #PROGRAMME DE DEFENCE LVL1#")
    print("Tu la prends.")
    ajouter_item("cle_usb_defence_lvl1")

    if a_item("robot_charge"):
        choix4 = select_avec_menu(
            "Veux-tu la brancher sur ton robot ?",
            ["OUI", "NON"]
        )
        if choix4 == "OUI":
            retirer_item("robot_charge")
            retirer_item("cle_usb_defence_lvl1")
            print("Tu insères la clé dans ton robot.")
            time.sleep(2)
            ajouter_item("robot_defensif_lvl1")
            print("#MISE À JOUR TERMINÉE#")
            time.sleep(2)
        print("Tu continues ton chemin.")
        time.sleep(1)

    print("\nUn scientifique surgit de derrière une cloison !")
    time.sleep(1)
    combat("Sientifique")
    print("Tu arrives à le battre et une porte s'ouvre derrière lui.")
    print("Sur cette porte il est écrit #CHEF DU NIVEAU#")

    choix5 = select_avec_menu("Entrer ?", ["OUI"])
    if choix5 == "OUI":
        print("Tu entres dans la salle du boss.")
        time.sleep(1)
        print("Le Scientifique fou se retourne vers toi... Le combat commence !")
        time.sleep(1)
        combat("Boss_LVL-1")
        print("\nBravo tu as battu le boss de l'étage -1 !")
        time.sleep(1)
        print("Tu récupères sur la carcasse du boss une carte d'accès et une seringue explosive...")
        ajouter_item("carte_acces_lvl2")
        ajouter_item("Serigue explosive")
        ajouter_item("kit_soin", 2)
        ajouter_item("Seringue soignante", 3)
        print("Bravo tu as fini le LVL-1 !")
        gagner_xp(550)

    joueur["etape"] = 5
    sauvegarder()  # ← CORRECTIF : sauvegarde avant de passer à l'étape 5

    choix6 = select_avec_menu("Aller à l'ascenseur ?", ["OUI"])
    print("Tu descends vers le -2...")
    time.sleep(4)


def etape_5():
    print("Tu arrives dans un couloir à l'ambiance joyeuse, tous les scientifiques travaillent ensemble.")
    time.sleep(1)
    print("Heu.. attend... LES SCIENTIFIQUES ?!")
    time.sleep(1)
    print("Ils te voient et sortent une arme.")
    time.sleep(1)
    combat("Horde de sientifiques")
    print("...")
    print("##SUITE DU JEU EN COURS DE DÉVELOPPEMENT##")


# ==========================================
# BOUCLE PRINCIPALE
# ==========================================

ETAPES = {
    0: etape_0,
    1: etape_1,
    2: etape_2,
    3: etape_3,
    4: etape_4,
    5: etape_5,
}

while True:
    etape_actuelle = joueur["etape"]
    if etape_actuelle in ETAPES:
        ETAPES[etape_actuelle]()
    else:
        print(f"\n⚙️ Étape {etape_actuelle} non encore disponible. À bientôt !")
        break