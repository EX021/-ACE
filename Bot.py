import discord
from discord.ext import commands
from discord.ui import Select, View, Button
import asyncio  
import datetime 
import time 
import os

TOKEN = os.getenv("DISCORD_TOKEN")



bot = commands.Bot(command_prefix="$", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot connecté sous le nom de : {bot.user.name}")
    # Ajout des vues persistantes pour que les boutons fonctionnent même après un reboot du bot
    bot.add_view(TicketView())

@bot.command(name="qotd")
@commands.has_permissions(manage_messages=True)
async def question_of_the_day(ctx, *, question: str):
    await ctx.message.delete() # Supprime le message de commande
    
    embed = discord.Embed(
        title="💬 QUESTION DU JOUR",
        description=f"**{question}**\n\nDonnez votre avis en dessous ! 👇",
        color=discord.Color.orange()
    )
    embed.set_footer(text=f"Proposée par {ctx.author.display_name}")
    
    msg = await ctx.send(content="@everyone", embed=embed)
    # Ajoute des réactions de base pour pousser à l'interaction
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")

class RoleButton(discord.ui.View):
    def __init__(self, role_id):
        super().__init__(timeout=None)
        self.role_id = role_id

    @discord.ui.button(label="Obtenir le rôle", style=discord.ButtonStyle.green)
    async def get_role(self, interaction: discord.Interaction, button: discord.ui.Button):

        role = interaction.guild.get_role(self.role_id)

        if role is None:
            return await interaction.response.send_message(
                "❌ Rôle introuvable.",
                ephemeral=True
            )

        member = interaction.user

        if role in member.roles:
            await member.remove_roles(role)
            await interaction.response.send_message(
                f"➖ Le rôle **{role.name}** a été retiré.",
                ephemeral=True
            )
        else:
            await member.add_roles(role)
            await interaction.response.send_message(
                f"➕ Le rôle **{role.name}** a été ajouté.",
                ephemeral=True
            )


@bot.command()
@commands.has_permissions(administrator=True)
async def rolebutton(ctx, role: discord.Role):

    embed = discord.Embed(
        title="🎭 Attribution de rôle",
        description=f"Clique sur le bouton pour obtenir **{role.name}**.",
        color=discord.Color.blue()
    )

    await ctx.send(
        embed=embed,
        view=RoleButton(role.id)
    )

@bot.command(name="lock")
@commands.has_permissions(manage_channels=True)
async def lock_channel(ctx):
    await ctx.message.delete()
    # Récupère le rôle @everyone (les membres de base)
    everyone = ctx.guild.default_role
    
    # Interdit l'envoi de messages pour ce salon
    await ctx.channel.set_permissions(everyone, send_messages=False)
    
    embed = discord.Embed(
        title="🔒 Salon Verrouillé",
        description="Ce salon a été temporairement fermé par le Staff. Merci de patienter.",
        color=discord.Color.red()
    )
    await ctx.send(embed=embed)

@bot.command(name="unlock")
@commands.has_permissions(manage_channels=True)
async def unlock_channel(ctx):
    await ctx.message.delete()
    everyone = ctx.guild.default_role
    
    # Rétablit la permission d'envoyer des messages (Neutre / Hérité)
    await ctx.channel.set_permissions(everyone, send_messages=None)
    
    embed = discord.Embed(
        title="🔓 Salon Déverrouillé",
        description="Le salon est de nouveau accessible. Bon chat à tous !",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command(name="say")
@commands.has_permissions(manage_messages=True)
async def say_embed(ctx, titre: str, *, message: str):
    await ctx.message.delete()
    await ctx.message.delete() # Supprime la commande du modérateur pour la discrétion
    
    embed = discord.Embed(
        title=titre,
        description=message.replace(r'\n', '\n'), # Permet de faire des retours à la ligne avec \n
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"Annonce officielle — {ctx.guild.name}")
    
    await ctx.send(embed=embed)

# ==========================================
# 🛑 SYSTÈME DE MODÉRATION PAR RÔLES (WARN, CANCEL & CREATEWARN)
# ==========================================

HIERARCHIE_SANCTIONS = [
    {"name": "warn1", "color": discord.Color.light_grey()},
    {"name": "warn2", "color": discord.Color.dark_grey()},
    {"name": "FG !", "color": discord.Color.red()},
    {"name": "!!", "color": discord.Color.dark_red()},
    {"name": "!!!", "color": discord.Color.from_rgb(1, 1, 1)} # Noir pur pour l'échelon max
]

@bot.command(name="createwarn")
@commands.has_permissions(administrator=True)
async def create_all_warn_roles(ctx):
    status_message = await ctx.send("🔨 Création des rôles de modération et de sanctions (`warn` & `FG`)...")

    for sanction_data in HIERARCHIE_SANCTIONS:
        existing_role = discord.utils.get(ctx.guild.roles, name=sanction_data["name"])
        
        if not existing_role:
            try:
                await ctx.guild.create_role(
                    name=sanction_data["name"],
                    color=sanction_data["color"],
                    reason="Création automatique du système de sanctions"
                )
            except discord.Forbidden:
                await ctx.send("❌ Permissions insuffisantes pour créer les rôles de sanctions.")
                return

    await status_message.edit(content="✅ Tous les rôles de modération (`warn1`, `warn2`, `FG !`, `!!`, `!!!`) ont été créés et sont prêts à l'emploi !")


@bot.command(name="warn")
@commands.has_permissions(manage_messages=True)
async def warn_member(ctx, member: discord.Member, *, raison: str = "Aucune raison fournie"):
    await ctx.message.delete()
    w1 = discord.utils.get(ctx.guild.roles, name="warn1")
    w2 = discord.utils.get(ctx.guild.roles, name="warn2")
    
    if not w1 or not w2:
        await ctx.send("❌ Erreur : Les rôles `warn1` et `warn2` doivent exister sur le serveur. Utilise `$createwarn` d'abord.")
        return

    if w2 in member.roles:
        await ctx.send(f"🚨 {member.mention} a reçu son 3ème avertissement ! Lancement de la procédure de Faute Grave...")
        await ctx.invoke(bot.get_command('cancel'), member=member, raison=f"Cumul de 3 avertissements (Dernier : {raison})")
        
    elif w1 in member.roles:
        await member.remove_roles(w1)
        await member.add_roles(w2)
        await ctx.send(f"⚠️ {member.mention} a reçu son 2ème avertissement. Rôle `warn2` attribué.\n**Raison :** {raison}")
        try:
            await member.send(f"⚠️ Vous avez reçu un 2ème avertissement sur **{ctx.guild.name}**.\n**Raison :** {raison}\n*Attention, le prochain warn déclenchera une destitution (Faute Grave).*")
        except: pass
        
    else:
        await member.add_roles(w1)
        await ctx.send(f"⚠️ {member.mention} a reçu son 1er avertissement. Rôle `warn1` attribué.\n**Raison :** {raison}")
        try:
            await member.send(f"⚠️ Vous avez reçu un avertissement sur **{ctx.guild.name}**.\n**Raison :** {raison} (1/3)")
        except: pass


@bot.command(name="cancel")
@commands.has_permissions(administrator=True)
async def cancel_member(ctx, member: discord.Member, *, raison: str = "Faute grave commise"):
    await ctx.message.delete()
    fg1 = discord.utils.get(ctx.guild.roles, name="FG !")
    fg2 = discord.utils.get(ctx.guild.roles, name="!!")
    fg3 = discord.utils.get(ctx.guild.roles, name="!!!")
    
    if not fg1 or not fg2 or not fg3:
        await ctx.send("❌ Erreur : Les rôles `FG !`, `!!` et `!!!` doivent exister sur le serveur. Utilise `$createwarn` d'abord.")
        return

    roles_a_retirer = [role for role in member.roles if role != ctx.guild.default_role and role < ctx.guild.me.top_role]
    
    try:
        if fg3 in member.roles:
            await ctx.send(f"🔨 Échelon maximal atteint pour {member.mention}. Prononciation du **BAN DÉFINITIF**.")
            try:
                await member.send(f"🔨 Vous avez été banni définitivement de **{ctx.guild.name}** suite à une accumulation de fautes graves récidivées.")
            except: pass
            await member.ban(reason=f"Récidive ultime de Faute Grave après !!! : {raison}")
            return

        elif fg2 in member.roles:
            await member.remove_roles(*roles_a_retirer)
            await member.add_roles(fg3)
            statut_fg = "!!! (Dernière chance avant Ban)"
            couleur_embed = discord.Color.from_rgb(1, 1, 1)
            
        elif fg1 in member.roles:
            await member.remove_roles(*roles_a_retirer)
            await member.add_roles(fg2)
            statut_fg = "!! (Récidive Lourde)"
            couleur_embed = discord.Color.dark_red()
            
        else:
            await member.remove_roles(*roles_a_retirer)
            await member.add_roles(fg1)
            statut_fg = "FG ! (Faute Grave)"
            couleur_embed = discord.Color.red()

        embed = discord.Embed(
            title="⚡ Sanction Appliquée : Destitution totale",
            description=f"Tous les grades de {member.mention} ont été révoqués suite à une faute grave.",
            color=couleur_embed
        )
        embed.add_field(name="Membre", value=member.mention, inline=True)
        embed.add_field(name="Niveau d'Infraction", value=f"⬛ **{statut_fg}**", inline=True)
        embed.add_field(name="Raison du dossier", value=raison, inline=False)
        embed.set_footer(text=f"Action demandée par {ctx.author.name}")
        
        await ctx.send(embed=embed)
        
        rapport_channel = discord.utils.get(ctx.guild.text_channels, name="rapport")
        if rapport_channel:
            await rapport_channel.send(embed=embed)

        try:
            await member.send(f"⚡ Vos rôles ont été supprimés sur **{ctx.guild.name}** et vous avez reçu le grade permanent **{statut_fg}**.\n**Raison :** {raison}")
        except: pass

    except discord.Forbidden:
        await ctx.send("❌ Le bot n'a pas les permissions hiérarchiques suffisantes pour modifier ce membre.")

# ==========================================
# 👔 BOUT 1 : COMMANDE $createstaff AMÉLIORÉE
# ==========================================

HIERARCHIE_STAFF = [
    {"name": "Fondateur", "chan": "👑・owners", "color": discord.Color.from_rgb(1, 1, 1)},
    {"name": "Administrateur", "chan": "🛡️・admins", "color": discord.Color.red()},
    {"name": "Responsable Staff", "chan": "👑・responsable-staff", "color": discord.Color.orange()},
    {"name": "Modérateur +", "chan": "⚔️・moderateurs-plus", "color": discord.Color.yellow()},
    {"name": "gestion abus", "chan": "🔮・gestion-abus", "color": discord.Color.purple()},
    {"name": "gestion staff", "chan": "🔷・gestion-staff", "color": discord.Color.blue()},
    {"name": "gestion Aide", "chan": "🟢・gestion-aide", "color": discord.Color.green()},
    {"name": "Modérateur", "chan": "⚔️・moderateurs", "color": discord.Color.dark_teal()},
    {"name": "Assistant", "chan": "⚙️・assistant", "color": discord.Color.light_grey()},
    {"name": "Staff Test", "chan": "🛟・staff-test", "color": discord.Color.from_rgb(255, 255, 255)}
]

@bot.command(name="createstaff")
@commands.has_permissions(administrator=True)
async def create_staff_ranks_and_channels(ctx):
    status_message = await ctx.send("🔨 Création de la hiérarchie Staff et des salons sécurisés...")

    # 1. Création ou récupération des rôles Staff
    for role_data in reversed(HIERARCHIE_STAFF):
        existing_role = discord.utils.get(ctx.guild.roles, name=role_data["name"])
        if not existing_role:
            try:
                await ctx.guild.create_role(name=role_data["name"], color=role_data["color"], reason="Staff Auto")
            except discord.Forbidden:
                await ctx.send("❌ Permissions insuffisantes pour créer les rôles.")
                return

    # 2. Création de la catégorie Staff
    category = discord.utils.get(ctx.guild.categories, name="👔 STAFF")
    if not category:
        category = await ctx.guild.create_category(name="👔 STAFF")

    # Rôles absolus prioritaires (Owners / Fondateurs)
    owner_role = discord.utils.get(ctx.guild.roles, name="Owner")
    fondateur_role = discord.utils.get(ctx.guild.roles, name="Fondateur")

    # 3. Création des salons avec permissions ultra-strictes
    for role_data in HIERARCHIE_STAFF:
        target_role = discord.utils.get(ctx.guild.roles, name=role_data["name"])
        
        # Configuration des permissions du salon
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False), # Tout le monde est bloqué
            ctx.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True) # Le bot
        }
        
        # On autorise les rôles absolus s'ils existent
        if owner_role: overwrites[owner_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        if fondateur_role: overwrites[fondateur_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        
        # On autorise le SEUL rôle concerné par ce salon
        if target_role: overwrites[target_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        # Création du salon textuel s'il n'existe pas
        chan_name = role_data["chan"]
        existing_text = discord.utils.get(category.text_channels, name=chan_name)
        if not existing_text:
            await ctx.guild.create_text_channel(name=chan_name, category=category, overwrites=overwrites)

        # Création du salon vocal s'il n'existe pas
        existing_voice = discord.utils.get(category.voice_channels, name=chan_name)
        if not existing_voice:
            await ctx.guild.create_voice_channel(name=chan_name, category=category, overwrites=overwrites)

    await status_message.edit(content="✅ La catégorie `👔 STAFF`, ses rôles uniques et ses salons sécurisés par grade ont été créés !")

# ==========================================
# 👑 BOUT 2 : COMMANDE $createrank COMPLÈTE
# ==========================================

HIERARCHIE_ROLES = [
    {"name": "Suzerain", "color": discord.Color.from_rgb(1, 1, 1)},
    {"name": "Rang Nation", "color": discord.Color.red()},
    {"name": "Influence", "color": discord.Color.blue()},
    {"name": "Origine", "color": discord.Color.green()},
    {"name": "Kama", "color": discord.Color.gold()},
    {"name": "All Stars", "color": discord.Color.orange()},
    {"name": "Classe S", "color": discord.Color.red()},
    {"name": "Damocles", "color": discord.Color.purple()},
    {"name": "FOwner", "color": discord.Color.from_rgb(139, 0, 0)},
    {"name": "Co-fOwner", "color": discord.Color.magenta()},
    {"name": "Capitaine", "color": discord.Color.teal()},
    {"name": "Vice-Capitaine", "color": discord.Color.dark_teal()},
    {"name": "Confirmé", "color": discord.Color.yellow()},
    {"name": "Test", "color": discord.Color.light_grey()},
    {"name": "Légende", "color": discord.Color.dark_gold()},
    {"name": "Diamant", "color": discord.Color.blue()},
    {"name": "Or", "color": discord.Color.gold()},
    {"name": "Argent", "color": discord.Color.light_grey()},
    {"name": "Bronze", "color": discord.Color.orange()},
    {"name": "Bavard", "color": discord.Color.dark_blue()},
    {"name": "Nouveau", "color": discord.Color.dark_green()},
    {"name": "@member", "color": discord.Color.from_rgb(255, 255, 255)}
]

@bot.command(name="createrank")
@commands.has_permissions(administrator=True)
async def create_all_ranks_and_channels(ctx):
    status_message = await ctx.send("🔨 Création de la hiérarchie des Rangs et des salons communautaires...")

    # 1. Création ou récupération des rôles de niveau
    for role_data in reversed(HIERARCHIE_ROLES):
        existing_role = discord.utils.get(ctx.guild.roles, name=role_data["name"])
        if not existing_role:
            try:
                await ctx.guild.create_role(name=role_data["name"], color=role_data["color"], reason="Ranks Auto")
            except discord.Forbidden:
                await ctx.send("❌ Le bot ne peut pas créer de rôles.")
                return

    # 2. Création de la catégorie Rangs
    category = discord.utils.get(ctx.guild.categories, name="👑 RANGS ÉVOLUTIFS")
    if not category:
        category = await ctx.guild.create_category(name="👑 RANGS ÉVOLUTIFS")

    # Liste des noms des rôles de modération via ton système de "&"
    STAFF_PERMS_NAMES = ["&Perm 4", "&Perm 5", "&Perm 6", "&Perm 7", "&Perm 8", "&Perm 9"]

    # 3. Création d'un salon par Rang avec accès au Staff de modération
    for role_data in HIERARCHIE_ROLES:
        if role_data["name"] == "@member":
            continue # Pas besoin de créer un salon pour @member
            
        rank_role = discord.utils.get(ctx.guild.roles, name=role_data["name"])
        
        # Configuration de base : personne ne voit le salon
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        # On autorise le rôle spécifique de ce rang
        if rank_role:
            overwrites[rank_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
            
        # On autorise automatiquement TOUS les rôles de permissions commençant par "&" (du Perm 4 au Perm 9)
        for perm_name in STAFF_PERMS_NAMES:
            staff_perm_role = discord.utils.get(ctx.guild.roles, name=perm_name)
            if staff_perm_role:
                overwrites[staff_perm_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        # Création propre du nom de salon (Ex: Suzerain -> 👑・suzerain)
        clean_chan_name = f"👑・{role_data['name'].lower().replace(' ', '-')}"
        
        existing_channel = discord.utils.get(category.text_channels, name=clean_chan_name)
        if not existing_channel:
            await ctx.guild.create_text_channel(name=clean_chan_name, category=category, overwrites=overwrites)

    await status_message.edit(content="✅ La catégorie `👑 RANGS ÉVOLUTIFS` et ses salons exclusifs ont été configurés ! (Seul le grade correspondant et les rôles `&Perm 4` à `&Perm 9` peuvent les voir).")

# ==========================================
# 🛡️ BOUT 3 : COMMANDE $createperm CORRIGÉE (AVEC PERMISSIONS)
# ==========================================

# Configuration des permissions Discord pures pour chaque niveau
perm_lvl_9 = discord.Permissions(administrator=True)

perm_lvl_8 = discord.Permissions(
    manage_guild=True,
    manage_channels=True,
    manage_roles=True,
    kick_members=True,
    ban_members=True,
    moderate_members=True,  # Permet de mettre en sourdine (Timeout)
    manage_messages=True
)

perm_lvl_7 = discord.Permissions(
    kick_members=True,
    ban_members=True,
    manage_messages=True,
    mute_members=True,     # Rendre muet en vocal
    deafen_members=True,   # Mettre sourd en vocal
    move_members=True      # Déplacer de salon vocal
)

perm_lvl_6 = discord.Permissions(
    kick_members=True,
    manage_messages=True,
    mute_members=True,
    deafen_members=True,
    move_members=True
)

perm_lvl_5 = discord.Permissions(
    manage_messages=True,
    moderate_members=True,
    move_members=True
)

perm_lvl_4 = discord.Permissions(
    manage_messages=True
)

# Les rôles de sanctions n'ont pas de permissions supplémentaires (Neutre)
perm_neutre = discord.Permissions.none()

HIERARCHIE_PERMS = [
    {"name": "&Perm 9", "color": discord.Color.from_rgb(1, 1, 1), "perms": perm_lvl_9},
    {"name": "&Perm 8", "color": discord.Color.from_rgb(255, 100, 100), "perms": perm_lvl_8},
    {"name": "&Perm 7", "color": discord.Color.from_rgb(255, 150, 0), "perms": perm_lvl_7},
    {"name": "&Perm 6", "color": discord.Color.from_rgb(255, 200, 0), "perms": perm_lvl_6},
    {"name": "&Perm 5", "color": discord.Color.from_rgb(200, 255, 0), "perms": perm_lvl_5},
    {"name": "&Perm 4", "color": discord.Color.from_rgb(0, 255, 200), "perms": perm_lvl_4},
    {"name": "&Perm 2", "color": discord.Color.from_rgb(120, 120, 120), "perms": perm_neutre},
    {"name": "&Perm 1", "color": discord.Color.from_rgb(180, 180, 180), "perms": perm_neutre}
]

@bot.command(name="createperm")
@commands.has_permissions(administrator=True)
async def create_all_permissions_roles(ctx):
    status_message = await ctx.send("🔨 Création des rôles de permissions structurels avec configurations d'accès...")

    for perm_data in reversed(HIERARCHIE_PERMS):
        existing_role = discord.utils.get(ctx.guild.roles, name=perm_data["name"])
        
        # Si le rôle n'existe pas, on le crée avec sa couleur et ses pouvoirs Discord
        if not existing_role:
            try:
                await ctx.guild.create_role(
                    name=perm_data["name"],
                    color=perm_data["color"],
                    permissions=perm_data["perms"], # Injection automatique des pouvoirs Discord
                    reason="Création automatique des rôles de permissions"
                )
            except discord.Forbidden:
                await ctx.send("❌ Permissions insuffisantes pour créer ou configurer les rôles de permissions.")
                return
        else:
            # Si le rôle existe déjà, on met à jour ses permissions au cas où
            try:
                await existing_role.edit(permissions=perm_data["perms"])
            except discord.Forbidden:
                pass

    await status_message.edit(content="✅ Tous les rôles structurels (`&Perm 1` à `&Perm 9`) ont été créés et configurés avec leurs permissions Discord respectives !")

# ==========================================
# 🎉 BOUT 5 : SYSTÈME DE GIVEAWAY MODERNE (AVEC BOUTON)
# ==========================================

class GiveawayView(discord.ui.View):
    def __init__(self, prix: str):
        super().__init__(timeout=None) # Rend le bouton persistant
        self.prix = prix
        self.participants = [] # Liste pour stocker les IDs des participants

    @discord.ui.button(label="Participer ! 🎉", style=discord.ButtonStyle.blurple, custom_id="giveaway_join")
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user
        
        if user.id in self.participants:
            # Si le membre a déjà cliqué, on lui retire sa participation (système toggle)
            self.participants.remove(user.id)
            await interaction.response.send_message("❌ Tu t'es retiré du giveaway.", ephemeral=True)
        else:
            # Sinon, on l'ajoute
            self.participants.append(user.id)
            await interaction.response.send_message("✅ Ta participation a été prise en compte ! Bonne chance. 🎉", ephemeral=True)

@bot.command(name="giveaway")
@commands.has_permissions(manage_guild=True)
async def start_giveaway(ctx, temps: str, *, prix: str):
    await ctx.message.delete()
    """Lance un giveaway. Exemple : $giveaway 10m Nitro Boost"""
    
    # Conversion basique du temps (s pour secondes, m pour minutes, h pour heures)
    temps_secondes = 0
    try:
        if temps.endswith("s"):
            temps_secondes = int(temps[:-1])
        elif temps.endswith("m"):
            temps_secondes = int(temps[:-1]) * 60
        elif temps.endswith("h"):
            temps_secondes = int(temps[:-1]) * 3600
        else:
            temps_secondes = int(temps) * 60 # Par défaut en minutes si pas d'unité
    except ValueError:
        await ctx.send("❌ Format de temps invalide ! Utilise par exemple `10m` (10 minutes) ou `2h` (2 heures).")
        return

    # Calcul du moment de la fin pour l'affichage Discord dynamique
    fin_timestamp = int(datetime.datetime.now().timestamp() + temps_secondes)

    embed = discord.Embed(
        title=f"🎉 GIVEAWAY STYLÉ : {prix} 🎉",
        description=f"Cliquez sur le bouton ci-dessous pour participer !\n\n⏳ **Fin du concours :** <t:{fin_timestamp}:R>",
        color=discord.Color.from_rgb(255, 100, 200)
    )
    embed.set_footer(text=f"Lancé par {ctx.author.name}")

    view = GiveawayView(prix=prix)
    giveaway_message = await ctx.send(embed=embed, view=view)

    # On attend la fin du compte à rebours
    await asyncio.sleep(temps_secondes)

    # Fin du giveaway : Tirage au sort
    if not view.participants:
        embed_fin = discord.Embed(
            title=f"🎉 GIVEAWAY TERMINÉ : {prix} 🎉",
            description="❌ Malheureusement, personne n'a participé au concours.",
            color=discord.Color.red()
        )
        await giveaway_message.edit(embed=embed_fin, view=None) # On supprime le bouton
        return

    import random
    gagnant_id = random.choice(view.participants)
    gagnant = ctx.guild.get_member(gagnant_id)

    # Affichage du gagnant
    embed_gagnant = discord.Embed(
        title=f"🎉 GIVEAWAY TERMINÉ : {prix} 🎉",
        description=f"🏆 **Gagnant :** {gagnant.mention if gagnant else f'<@{gagnant_id}>'}\n\nFélicitations à lui !",
        color=discord.Color.green()
    )
    await giveaway_message.edit(embed=embed_gagnant, view=None)
    await ctx.send(f"🥳 Félicitations à {gagnant.mention if gagnant else f'<@{gagnant_id}>'} qui remporte **{prix}** !")

# ==========================================
# 🔧 GESTION DES SALONS
# ==========================================

@bot.command(name="reboot")
@commands.has_permissions(manage_channels=True)
async def reboot_channel(ctx, target: str = None):
    await ctx.message.delete()
    if target == "channel":
        current_channel = ctx.channel
        position = current_channel.position
        category = current_channel.category
        new_channel = await current_channel.clone(reason="Reboot du salon")
        await current_channel.delete()
        await new_channel.edit(position=position, category=category)
        await new_channel.send("🔄 Le salon a été réinitialisé avec succès !")

@bot.command(name="del")
@commands.has_permissions(manage_channels=True)
async def delete_channel(ctx, target: str = None):
    await ctx.message.delete()
    if target == "channel":
        await ctx.channel.send("🚨 Suppression du salon dans 3 secondes...")
        await asyncio.sleep(3)
        await ctx.channel.delete()

@bot.command(name="rename")
@commands.has_permissions(manage_channels=True)
async def rename_channel(ctx, *, new_name: str):
    await ctx.message.delete()
    clean_name = new_name.lower().replace(" ", "-")
    old_name = ctx.channel.name
    await ctx.channel.edit(name=clean_name)
    
    embed = discord.Embed(
        description=f"📝 Salon renommé avec succès !\n**Ancien nom :** `{old_name}`\n**Nouveau nom :** `{clean_name}`",
        color=discord.Color.orange()
    )
    await ctx.send(embed=embed)

# ==========================================
# 🎭 GESTION DES RÔLES (CORRIGÉE POUR LE SYSTÈME &)
# ==========================================

@bot.command(name="addrole")
@commands.has_permissions(manage_roles=True)
async def addrole(ctx, member: discord.Member, *, role_input: str):
    await ctx.message.delete()
    # Nettoyage si Discord envoie une mention brute de rôle
    if role_input.startswith("<@&") and role_input.endswith(">"):
        role_id = int(role_input.replace("<@&", "").replace(">", ""))
        role = discord.utils.get(ctx.guild.roles, id=role_id)
    elif role_input.isdigit():
        role = discord.utils.get(ctx.guild.roles, id=int(role_input))
    else:
        # Recherche intelligente : insensible aux majuscules et espaces
        role = discord.utils.find(lambda r: r.name.lower().strip() == role_input.lower().strip(), ctx.guild.roles)

    if not role:
        await ctx.send(f"❌ Impossible de trouver le rôle `{role_input}`. Vérifie l'orthographe.")
        return

    try:
        await member.add_roles(role)
        await ctx.send(f"✅ Le rôle **{role.name}** a été ajouté à {member.mention}.")
    except discord.Forbidden:
        await ctx.send("❌ Je n'Avez pas les permissions nécessaires (place mon rôle plus haut dans les paramètres du serveur).")

@bot.command(name="delrole")
@commands.has_permissions(manage_roles=True)
async def delrole(ctx, member: discord.Member, *, role_input: str):
    await ctx.message.delete()
    if role_input.startswith("<@&") and role_input.endswith(">"):
        role_id = int(role_input.replace("<@&", "").replace(">", ""))
        role = discord.utils.get(ctx.guild.roles, id=role_id)
    elif role_input.isdigit():
        role = discord.utils.get(ctx.guild.roles, id=int(role_input))
    else:
        role = discord.utils.find(lambda r: r.name.lower().strip() == role_input.lower().strip(), ctx.guild.roles)

    if not role:
        await ctx.send(f"❌ Impossible de trouver le rôle `{role_input}`.")
        return

    try:
        await member.remove_roles(role)
        await ctx.send(f"❌ Le rôle **{role.name}** a été retiré à {member.mention}.")
    except discord.Forbidden:
        await ctx.send("❌ Je n'ai pas les permissions nécessaires pour modifier ce rôle.")

# ==========================================
# 📊 STATISTIQUES PROFILE
# ==========================================

@bot.command(name="su")
async def user_stats(ctx, member: discord.Member = None):
    await ctx.message.delete()
    member = member or ctx.author
    progress_message = await ctx.send("📊 Calcul des statistiques en cours...")
    
    message_count = 0
    for channel in ctx.guild.text_channels:
        if channel.permissions_for(ctx.guild.me).read_message_history:
            try:
                async for msg in channel.history(limit=1000):
                    if msg.author.id == member.id:
                        message_count += 1
            except Exception: continue

    vocal_status = f"🎙️ Connecté dans : {member.voice.channel.name}" if member.voice and member.voice.channel else "🤫 Déconnecté"

    roles = [role.mention for role in member.roles if role != ctx.guild.default_role]
    roles_display = ", ".join(roles) if roles else "Aucun rôle"
    
    embed = discord.Embed(title=f"📊 Stats de {member.display_name}", color=member.color)
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="Nom d'utilisateur", value=member.name, inline=True)
    embed.add_field(name="ID Discord", value=f"`{member.id}`", inline=True)
    embed.add_field(name="Messages envoyés (récents)", value=f"💬 `{message_count}` messages", inline=True)
    embed.add_field(name="Statut Vocal", value=vocal_status, inline=True)
    embed.add_field(name="Création du compte", value=f"<t:{int(member.created_at.timestamp())}:R>", inline=True)
    embed.add_field(name="Arrivée sur le serveur", value=f"<t:{int(member.joined_at.timestamp())}:R>", inline=True)
    embed.add_field(name=f"Rôles ({len(roles)})", value=roles_display, inline=False)
    embed.set_footer(text=f"Demandé par {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
    
    await progress_message.delete()
    await ctx.send(embed=embed)

# ==========================================
# 🎟️ SYSTÈME DE TICKETS & RECRUTEMENT
# ==========================================

@bot.command(name="addmember")
@commands.has_permissions(manage_channels=True)
async def add_to_ticket(ctx, member: discord.Member):
    await ctx.message.delete()
    if "ticket-" in ctx.channel.name or "recrut-" in ctx.channel.name:
        await ctx.channel.set_permissions(member, read_messages=True, send_messages=True)
        embed = discord.Embed(description=f"✅ {member.mention} a été ajouté au ticket.", color=discord.Color.green())
        await ctx.send(embed=embed)

@bot.command(name="delmember")
@commands.has_permissions(manage_channels=True)
async def remove_from_ticket(ctx, member: discord.Member):
    await ctx.message.delete()
    if "ticket-" in ctx.channel.name or "recrut-" in ctx.channel.name:
        await ctx.channel.set_permissions(member, overwrite=None)
        embed = discord.Embed(description=f"❌ {member.mention} a été retiré du ticket.", color=discord.Color.red())
        await ctx.send(embed=embed)

class TicketSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Rank up", description="Demande de montée en grade", emoji="📈"),
            discord.SelectOption(label="Signalement", description="Signaler un comportement", emoji="⚠️"),
            discord.SelectOption(label="Help", description="Demander de l'aide", emoji="❓")
        ]
        super().__init__(placeholder="Choisissez la raison du ticket...", options=options, custom_id="ticket_select")

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user
        choice = self.values[0]
        
        ping_role_name = "gestion staff" if choice == "Rank up" else "gestion abus" if choice == "Signalement" else "gestion Aide"
        role = discord.utils.get(guild.roles, name=ping_role_name)
        ping_mention = role.mention if role else f"@{ping_role_name}"

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
        }
        if role: overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        ticket_channel = await guild.create_text_channel(name=f"ticket-{choice.lower()}-{user.name}", category=interaction.channel.category, overwrites=overwrites)
        
        embed = discord.Embed(title="🎟️ Ticket Ouvert", color=discord.Color.blue())
        embed.add_field(name="Raison", value=choice, inline=False)
        embed.add_field(name="Auteur", value=user.mention, inline=False)
        embed.set_footer(text="[$]ACE - Système de Ticket")
        await ticket_channel.send(content=ping_mention, embed=embed)
        await interaction.response.send_message(f"✅ Ticket créé : {ticket_channel.mention}", ephemeral=True)

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

@bot.command()
async def ticket(ctx):
    await ctx.message.delete()
    embed = discord.Embed(title="🎟️ Support / Assistance", description="Ouvre un ticket via le menu ci-dessous.", color=discord.Color.blue())
    await ctx.send(embed=embed, view=TicketView())

class RecrutButton(View):
    def __init__(self, role_id):
        super().__init__(timeout=None)
        self.role_id = role_id

    @discord.ui.button(label="Postuler", style=discord.ButtonStyle.green, custom_id="btn_recrut")
    async def recrut_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        recrut_channel = await guild.create_text_channel(name=f"recrut-{user.name}", category=interaction.channel.category, overwrites=overwrites)
        await recrut_channel.send(f"Bienvenue {user.mention} !\nExplique tes motivations ici.")
        await interaction.response.send_message(f"✅ Salon créé : {recrut_channel.mention}", ephemeral=True)

@bot.command()
async def recrut(ctx, role: discord.Role):
    await ctx.message.delete() 
    embed = discord.Embed(title="📝 Recrutements Ouverts", description=f"Clique ci-dessous pour postuler au rôle **{role.name}** !", color=discord.Color.green())
    await ctx.send(embed=embed, view=RecrutButton(role.id))

@bot.command()
async def accept(ctx, member: discord.Member):
    try:
        await member.send(f"🎉 Félicitations ! Ta candidature sur **{ctx.guild.name}** a été acceptée !")
        await ctx.send(f"✅ Message d'acceptation envoyé à {member.mention}.")
    except discord.Forbidden: await ctx.send("❌ MP fermés.")

@bot.command()
async def refuse(ctx, member: discord.Member):
    try:
        await member.send(f"❌ Ta candidature sur **{ctx.guild.name}** a été refusée.")
        await ctx.send(f"✅ Message de refus envoyé à {member.mention}.")
    except discord.Forbidden: await ctx.send("❌ MP fermés.")

@bot.event
async def on_member_join(member):
    # Remplace par le nom exact de ton salon de bienvenue
    channel = discord.utils.get(member.guild.text_channels, name="👋┃bienvenue")
    if channel:
        embed = discord.Embed(
            title=f"👋 Bienvenue sur {member.guild.name} !",
            description=f"Installe-toi confortablement {member.mention} !\n\n"
                        f"📜 N'oublie pas de lire les règles.\n"
                        f"🎭 Prends tes rôles pour personnaliser ton profil.",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Nous sommes maintenant {member.guild.member_count} membres !")
        await channel.send(embed=embed)

bot.run(TOKEN)