from db import Database


class Texts:

    @staticmethod
    async def create_statistic(db: Database):
        characters = db.get_all_categories()
        users_count = db.get_users_count()

        text = '<b>Ститистика по кнопкам:</b>\n\n'
        for character in characters:
            text += f"<b>Кнопка:</b> {character.name} нажато - {character.use_count}\n"
        text += f'\n<b>Всего пользователей:</b> {users_count}'

        return text
