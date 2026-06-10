# cheat_live.py
import json, time

ITEMS_CHEAT = {
    "or":                   {"name": "Or",                        "type": "currency",        "qty": 999999999},
    "kit_soin":             {"name": "Kit de soin",               "type": "consumable",      "qty": 99, "heal": 50},
    "seringue_soignante":   {"name": "Seringue soignante",        "type": "consumable",      "qty": 99, "heal": 100},
    "pistolet":             {"name": "Pistolet",                  "type": "weapon",          "qty": 1,  "power": 999999},
    "fiole_occulte":        {"name": "Fiole d'énergie occulte",   "type": "resource_speciale","qty": 99},
    "lame_parasite":        {"name": "Lame parasite",             "type": "weapon",          "qty": 1,  "power": 999999, "cursed": True, "parasite": True, "niveau": 100, "evolution": "maitrisee", "rarity": "Légendaire"},
    "totem_immortalite":    {"name": "Totem d'immortalité",       "type": "totem",           "qty": 1,  "actif": True,  "evolution": "stabilise", "rarity": "Légendaire"},
    "armure_neant":         {"name": "Armure du Néant",           "type": "armor",           "qty": 1,  "actif": True,  "charges": 99, "evolution": "stabilisee", "rarity": "Légendaire"},
    "canon_antimatiere":    {"name": "Canon à antimatière",       "type": "weapon",          "qty": 1,  "power": 999999999},
    "katana_technologique": {"name": "Katana technologique",      "type": "weapon",          "qty": 1,  "power": 999999999},
}

while True:
    try:
        with open("sauvegarde.json", "r") as f:
            joueur = json.load(f)

        # ❤️ PV infinis
        joueur["pv"]      = 999999
        joueur["pv_max"]  = 999999

        # ⚔️ Dégâts max
        joueur["degats_base"] = 999999

        # ⭐ Niveau max
        joueur["niveau"] = 99
        joueur["xp"]     = 0

        # 🛡️ Artefacts actifs
        joueur["totem_actif"]    = True
        joueur["armure_charges"] = 99

        # 📦 Injecter tous les items
        for item_id, data in ITEMS_CHEAT.items():
            joueur["inventaire"][item_id] = data

        with open("sauvegarde.json", "w") as f:
            json.dump(joueur, f)

    except:
        pass

    time.sleep(2)