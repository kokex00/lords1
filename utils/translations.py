from datetime import datetime
import pytz

class Translations:
    """Handle translations and localization"""
    
    def __init__(self):
        self.translations = {
            'en': {
                'match_created': 'Match Created',
                'match_reminder': 'Match Reminder',
                'match_cancelled': 'Match Cancelled',
                'minutes_before': 'minutes before match',
                'match_time': 'Match Time',
                'participants': 'Participants',
                'description': 'Description',
                'creator': 'Creator',
                'server': 'Server',
                'reason': 'Reason',
                'no_permission': 'You do not have permission to use this command',
                'error': 'Error',
                'success': 'Success',
                'match_in': 'Match in',
                'cancelled_by': 'Cancelled by',
                'timezone_gmt': 'GMT',
                'join_match': 'You have been invited to a match!',
                'match_info': 'Match Information'
            },
            'ar': {
                'match_created': 'تم إنشاء المباراة',
                'match_reminder': 'تذكير المباراة',
                'match_cancelled': 'تم إلغاء المباراة',
                'minutes_before': 'دقائق قبل المباراة',
                'match_time': 'وقت المباراة',
                'participants': 'المشاركون',
                'description': 'الوصف',
                'creator': 'المنشئ',
                'server': 'السيرفر',
                'reason': 'السبب',
                'no_permission': 'ليس لديك صلاحية لاستخدام هذا الأمر',
                'error': 'خطأ',
                'success': 'نجح',
                'match_in': 'المباراة خلال',
                'cancelled_by': 'ألغيت بواسطة',
                'timezone_mecca': 'توقيت مكة',
                'join_match': 'تم دعوتك للمشاركة في مباراة!',
                'match_info': 'معلومات المباراة'
            },
            'pt': {
                'match_created': 'Partida Criada',
                'match_reminder': 'Lembrete da Partida',
                'match_cancelled': 'Partida Cancelada',
                'minutes_before': 'minutos antes da partida',
                'match_time': 'Horário da Partida',
                'participants': 'Participantes',
                'description': 'Descrição',
                'creator': 'Criador',
                'server': 'Servidor',
                'reason': 'Motivo',
                'no_permission': 'Você não tem permissão para usar este comando',
                'error': 'Erro',
                'success': 'Sucesso',
                'match_in': 'Partida em',
                'cancelled_by': 'Cancelado por',
                'timezone_br': 'Horário de Brasília',
                'join_match': 'Você foi convidado para uma partida!',
                'match_info': 'Informações da Partida'
            }
        }
    
    def get_text(self, key: str, language: str = 'en') -> str:
        """Get translated text"""
        return self.translations.get(language, self.translations['en']).get(key, key)
    
    def format_time_for_language(self, dt: datetime, language: str) -> str:
        """Format datetime according to language timezone"""
        if language == 'ar':
            # Mecca time (UTC+3)
            mecca_tz = pytz.timezone('Asia/Riyadh')
            local_time = dt.replace(tzinfo=pytz.UTC).astimezone(mecca_tz)
            return local_time.strftime('%Y-%m-%d %H:%M') + ' (توقيت مكة)'
        elif language == 'pt':
            # Brazil time (UTC-3)
            brazil_tz = pytz.timezone('America/Sao_Paulo')
            local_time = dt.replace(tzinfo=pytz.UTC).astimezone(brazil_tz)
            return local_time.strftime('%Y-%m-%d %H:%M') + ' (Horário de Brasília)'
        else:
            # GMT/UTC for English
            utc_time = dt.replace(tzinfo=pytz.UTC)
            return utc_time.strftime('%Y-%m-%d %H:%M') + ' GMT'
    
    def get_timezone_for_language(self, language: str) -> pytz.BaseTzInfo:
        """Get timezone object for language"""
        if language == 'ar':
            return pytz.timezone('Asia/Riyadh')
        elif language == 'pt':
            return pytz.timezone('America/Sao_Paulo')
        else:
            return pytz.UTC
    
    def get_language_flag(self, language: str) -> str:
        """Get flag emoji for language"""
        flags = {
            'en': '🇺🇸',
            'ar': '🇸🇦',
            'pt': '🇧🇷'
        }
        return flags.get(language, '🇺🇸')
    
    def get_language_name(self, language: str) -> str:
        """Get language name in its own language"""
        names = {
            'en': 'English',
            'ar': 'العربية',
            'pt': 'Português'
        }
        return names.get(language, 'English')
