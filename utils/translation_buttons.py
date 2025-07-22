import discord
from discord import ui
from utils.translations import Translations

class TranslationView(discord.ui.View):
    """Translation buttons for private messages"""
    
    def __init__(self, original_embed: discord.Embed, match_data: dict, current_language: str = 'en'):
        super().__init__(timeout=300)  # 5 minutes timeout
        self.original_embed = original_embed
        self.match_data = match_data
        self.current_language = current_language
        self.translations = Translations()
        
    @discord.ui.button(label='🇺🇸 English', style=discord.ButtonStyle.secondary, custom_id='translate_en')
    async def translate_english(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Translate to English"""
        if self.current_language == 'en':
            await interaction.response.send_message("Already in English!", ephemeral=True)
            return
            
        new_embed = self._create_translated_embed('en')
        await interaction.response.send_message(embed=new_embed, ephemeral=True)
    
    @discord.ui.button(label='🇸🇦 العربية', style=discord.ButtonStyle.secondary, custom_id='translate_ar')
    async def translate_arabic(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Translate to Arabic"""
        if self.current_language == 'ar':
            await interaction.response.send_message("الرسالة بالعربية بالفعل!", ephemeral=True)
            return
            
        new_embed = self._create_translated_embed('ar')
        await interaction.response.send_message(embed=new_embed, ephemeral=True)
    
    @discord.ui.button(label='🇧🇷 Português', style=discord.ButtonStyle.secondary, custom_id='translate_pt')
    async def translate_portuguese(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Translate to Portuguese"""
        if self.current_language == 'pt':
            await interaction.response.send_message("Já está em português!", ephemeral=True)
            return
            
        new_embed = self._create_translated_embed('pt')
        await interaction.response.send_message(embed=new_embed, ephemeral=True)
    
    def _create_translated_embed(self, language: str) -> discord.Embed:
        """Create a translated version of the embed"""
        from datetime import datetime
        
        # Get translations
        title = self.translations.get_text('match_info', language)
        match_time_text = self.translations.get_text('match_time', language)
        participants_text = self.translations.get_text('participants', language)
        creator_text = self.translations.get_text('creator', language)
        server_text = self.translations.get_text('server', language)
        
        # Create new embed
        embed = discord.Embed(
            title=f"⚔️ {title}",
            description=self.match_data.get('title', 'Match'),
            color=0x5865f2,
            timestamp=datetime.utcnow()
        )
        
        # Match time with timezone
        if self.match_data.get('time'):
            match_time = datetime.fromisoformat(self.match_data['time'])
            formatted_time = self.translations.format_time_for_language(match_time, language)
            
            embed.add_field(
                name=f"🕒 {match_time_text}",
                value=f"{formatted_time}\n<t:{int(match_time.timestamp())}:R>",
                inline=False
            )
        
        # Teams or participants
        if self.match_data.get('team1_mentions') and self.match_data.get('team2_mentions'):
            team1_text = "Team 1" if language == 'en' else "الفريق الأول" if language == 'ar' else "Equipe 1"
            team2_text = "Team 2" if language == 'en' else "الفريق الثاني" if language == 'ar' else "Equipe 2"
            
            embed.add_field(
                name=f"🔴 {team1_text}",
                value=self.match_data['team1_mentions'],
                inline=True
            )
            embed.add_field(
                name=f"🔵 {team2_text}",
                value=self.match_data['team2_mentions'],
                inline=True
            )
            embed.add_field(name="\u200b", value="\u200b", inline=True)
        else:
            embed.add_field(
                name=f"👥 {participants_text}",
                value=f"{len(self.match_data.get('participants', []))} members",
                inline=True
            )
        
        # Creator
        embed.add_field(
            name=f"👤 {creator_text}",
            value=f"<@{self.match_data.get('creator_id', '')}>",
            inline=True
        )
        
        # Description if available
        if self.match_data.get('description'):
            desc_text = self.translations.get_text('description', language)
            embed.add_field(
                name=f"📝 {desc_text}",
                value=self.match_data['description'],
                inline=False
            )
        
        return embed

class SimpleTranslationView(discord.ui.View):
    """Simple translation buttons for any embed"""
    
    def __init__(self, original_text: str, context: str = "message"):
        super().__init__(timeout=300)
        self.original_text = original_text
        self.context = context
        self.translations = Translations()
    
    @discord.ui.button(label='🇺🇸 EN', style=discord.ButtonStyle.secondary)
    async def translate_english(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Simple English response"""
        response = "This message is already in the server's language."
        await interaction.response.send_message(response, ephemeral=True)
    
    @discord.ui.button(label='🇸🇦 AR', style=discord.ButtonStyle.secondary)
    async def translate_arabic(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Simple Arabic response"""
        response = "هذه الرسالة بلغة السيرفر الأساسية."
        await interaction.response.send_message(response, ephemeral=True)
    
    @discord.ui.button(label='🇧🇷 PT', style=discord.ButtonStyle.secondary)
    async def translate_portuguese(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Simple Portuguese response"""
        response = "Esta mensagem está no idioma principal do servidor."
        await interaction.response.send_message(response, ephemeral=True)