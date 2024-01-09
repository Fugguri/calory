from datetime import datetime
import pymysql
from config import Config
from models import *


class Database:
    def __init__(self, cfg: Config):
        self.cfg: Config = cfg
        self.connection = pymysql.connect(
            host=self.cfg.tg_bot.host,
            user=self.cfg.tg_bot.user,
            port=self.cfg.tg_bot.port,
            password=self.cfg.tg_bot.password,
            database=self.cfg.tg_bot.database,
        )
        self.connection.autocommit(True)

    def cbdt(self):
        with self.connection.cursor() as cursor:
            create = """CREATE TABLE IF NOT EXISTS Users
                        (id INT PRIMARY KEY AUTO_INCREMENT,
                        telegram_id BIGINT UNIQUE NOT NULL ,
                        full_name TEXT,
                        username TEXT,
                        has_access BOOL DEFAULT false,
                        role TEXT DEFAULT 'USER',
                        weight INT,
                        height INT,
                        age INT,
                        sex TEXT,
                        activity TEXT,  
                        goal TEXT,
                        daily_calory INT
                        );"""
            cursor.execute(create)
            self.connection.commit()

        with self.connection.cursor() as cursor:
            create = """CREATE TABLE IF NOT EXISTS Records
                        (id INT PRIMARY KEY AUTO_INCREMENT,
                        telegram_id BIGINT,
                        dish TEXT,
                        protein TEXT,
                        calories TEXT,
                        grams TEXT,
                        carbs TEXT,
                        fats TEXT,
                        date TEXT
                        );"""
            cursor.execute(create)
            self.connection.commit()
        with self.connection.cursor() as cursor:
            create = """CREATE TABLE IF NOT EXISTS Promt
                        (id INT PRIMARY KEY AUTO_INCREMENT,
                        text TEXT
                        );"""
            cursor.execute(create)
            self.connection.commit()

        # with self.connection.cursor() as cursor:
        #     create =""" CREATE TABLE IF NOT EXISTS clients
        #             (id INT PRIMARY KEY AUTO_INCREMENT,
        #             user_id INT,
        #             api_id INT,
        #             api_hash TEXT,
        #             phone TEXT NOT NULL,
        #             ai_settings TEXT,
        #             mailing_text TEXT,
        #             answers BIGINT DEFAULT 0,
        #             gs TEXT UNIQUE ,
        #             is_active BOOL DEFAULT false,
        #             FOREIGN KEY(user_id) REFERENCES users(id) )"""
        #     cursor.execute(create)
        #     self.connection.commit()

    def add_user(self, user: User):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute("INSERT IGNORE INTO Users (full_name, telegram_id, username) VALUES (%s, %s, %s) ",
                           (user.full_name, user.id, user.username))
            self.connection.commit()
            self.connection.close()

    def add_user(self, promt):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute("INSERT IGNORE INTO Promt (text) VALUES (%s) ",
                           (promt))
            self.connection.commit()
            self.connection.close()

    def add_diary_record(self, telegram_id, food_data: FoodData):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute("INSERT IGNORE INTO Records (telegram_id,dish,protein,calories,grams,carbs,fats,date) VALUES (%s, %s, %s,%s, %s, %s, %s, %s) ",
                           (telegram_id,
                            food_data.dish,
                            food_data.protein,
                            int(food_data.calories),
                            food_data.grams,
                            food_data.carbs,
                            food_data.fats,
                            str(datetime.now().date())))
            self.connection.commit()
            self.connection.close()

    def get_all_users(self):
        result = []
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                """SELECT * FROM Users""")
            res = cursor.fetchall()
            self.connection.commit()
            self.connection.close()
            for user in res:
                result.append(User(*user))
        return result

    def get_amount_daily_records(self, telegram_id):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                """SELECT * FROM Records WHERE date=%s and telegram_id=%s""", (datetime.now().date(), telegram_id))
            res = cursor.fetchall()
            result = 0
            for r in res:
                if r[4]:
                    result += int(r[4])

        return result

    def update_daily_calory(self, telegram_id, calory):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                """UPDATE Users SET daily_calory = %s WHERE telegram_id=%s""", (calory, telegram_id))
            cursor.fetchone()
            self.connection.commit()
            self.connection.close()

    def update_promt(self, promt):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                """UPDATE Promt SET text = %s WHERE id=%s""", (promt, 1))
            cursor.fetchone()
            self.connection.commit()
            self.connection.close()

    def update_user_data(self, telegram_id, settings: Settings):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                """UPDATE Users SET
                weight = %s,
                height = %s,
                age = %s,
                activity= %s, 
                sex= %s, 
                goal= %s
                WHERE telegram_id=%s""", (settings.weight,
                                          settings.height,
                                          settings.age,
                                          settings.activity,
                                          settings.sex,
                                          settings.goal,
                                          telegram_id))
            cursor.fetchone()
            self.connection.commit()
            self.connection.close()

    def get_user(self, telegram_id):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                """SELECT *
                FROM Users
                WHERE telegram_id=%s""", (telegram_id,))
            res = cursor.fetchone()
            self.connection.commit()
            self.connection.close()
            user = User(*res)
        return user

    def get_promt(self):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                """SELECT text
                FROM Promt
                WHERE id=%s""", (1,))
            res = cursor.fetchone()
            self.connection.commit()
            self.connection.close()
        return res

    def get_users_count(self):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                """SELECT COUNT(*) FROM Users""")
            res = cursor.fetchone()
        return res[0]


if __name__ == "__main__":
    db = Database()
    from config.config import load_config

    config = load_config("config.json", "texts.yml")
    ch = Category(0, "Maria", "test", "test category", 164, 0)
    db.add_category(ch)
