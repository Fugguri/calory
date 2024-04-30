import datetime
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
                        free_diary_records INT DEFAULT 30,
                        weight INT,
                        height INT,
                        age INT,
                        sex TEXT,
                        activity TEXT,  
                        goal TEXT,
                        daily_calory INT,
                        discount INT DEFAULT 0,
                        subscription DATE,
                        name TEXT,
                        score INT
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
                        date TEXT,
                        score INT
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
        with self.connection.cursor() as cursor:
            create = """CREATE TABLE IF NOT EXISTS Promo
                        (id INT PRIMARY KEY AUTO_INCREMENT,
                        code TEXT UNIQUE NOT NULL,
                        percent INT,
                        amount BIGINT DEFAULT 0);"""
            cursor.execute(create)
            self.connection.commit()

    def add_promo(self, promo: Promo):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute("INSERT IGNORE INTO Promo (code, percent, amount) VALUES (%s, %s,%s) ",
                           (promo.code, promo.percent, promo.amount))
            self.connection.commit()
            self.connection.close()

    def get_promo_by_code(self, code: str):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Promo WHERE code=%s ", (code))
            res = cursor.fetchone()
            if res:
                return Promo(*res)
            return None

    def get_all_promo(self):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Promo ")
            res = cursor.fetchall()

            return [Promo(*r)for r in res]

    def add_user(self, user: User):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute("INSERT IGNORE INTO Users (full_name, telegram_id, username) VALUES (%s, %s, %s) ",
                           (user.full_name, user.id, user.username))
            self.connection.commit()
            self.connection.close()

    def add_promt(self, promt):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute("INSERT IGNORE INTO Promt (text) VALUES (%s) ",
                           (promt))
            self.connection.commit()
            self.connection.close()

    def add_diary_record(self, telegram_id, food_data: FoodData):
        print(food_data)
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute("INSERT IGNORE INTO Records (telegram_id,dish,protein,calories,grams,carbs,fats,date,score) VALUES (%s, %s, %s,%s, %s, %s, %s, %s,%s) ",
                           (telegram_id,
                            food_data.dish,
                            food_data.protein,
                            int(food_data.calories),
                            food_data.grams,
                            food_data.carbs,
                            food_data.fats,
                            str(datetime.datetime.now()),
                            food_data.score))
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
                """SELECT * FROM Records 
                WHERE Month(date) = Month(DATE(NOW()))
                AND Year(date) = Year(DATE(NOW()))
                AND Date(date)= Date(DATE(NOW()))
                and telegram_id=%s ORDER BY date""", (telegram_id))
            res = cursor.fetchall()
            print(res)
            datas: List[Record] = [Record(*data)for data in res]
            print(datas)
            result = 0
            for data in datas:
                if data.score:
                    result += int(data.score)

        return result

    def get_user_with_yesterday_records(self) -> UserWithYesterdayRecords:
        self.connection.ping()
        result: List[UserWithYesterdayRecords] = []
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Users")
            users = cursor.fetchall()
            users = [User(*user) for user in users]
            for user in users:

                cursor.execute(
                    """SELECT * FROM Records 
                    WHERE Month(date) = Month(DATE(NOW()))
                    AND Year(date) = Year(DATE(NOW()-1))
                    AND Date(date)= Date(DATE(NOW()-1))
                    and telegram_id=%s ORDER BY date
                    """, (user.user_id))
                records = cursor.fetchall()
                records = [Record(record) for record in records]
                result.append(UserWithYesterdayRecords(
                    user=user, records=records))

        return result

    def get_user_with_weekly_records(self) -> UserWithYesterdayRecords:
        self.connection.ping()
        result: List[UserWithYesterdayRecords] = []
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Users")

            users = cursor.fetchall()
            users = [User(*user) for user in users]

            for user in users:

                cursor.execute(
                    """SELECT * FROM Records 
                    WHERE Month(date) = Month(DATE(NOW()))
                    AND Year(date) = Year(DATE(NOW()-7))
                    AND Date(date)= Date(DATE(NOW()-7))
                    and telegram_id=%s ORDER BY date
                    """, (user.user_id))
                records = cursor.fetchall()
                records = [Record(record) for record in records]
                result.append(UserWithYesterdayRecords(
                    user=user, records=records))
        return result

    @staticmethod
    def add_one_month(orig_date):
        # advance year and month by one month
        new_year = orig_date.year
        new_month = orig_date.month + 1
        # note: in datetime.date, months go from 1 to 12
        if new_month > 12:
            new_year += 1
            new_month -= 12
        new_day = orig_date.day
        # while day is out of range for month, reduce by one
        while True:
            try:
                new_date = datetime.date(new_year, new_month, new_day)
            except ValueError as e:
                new_day -= 1
            else:
                break
        return new_date

    def set_month_subscription(self, telegram_id):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            end_date = self.add_one_month(datetime.date.today())
            cursor.execute(
                """UPDATE Users SET subscription = %s WHERE telegram_id=%s""", (end_date, telegram_id))
            cursor.fetchone()
            self.connection.commit()
            self.connection.close()

    def update_user_discount(self, telegram_id, discount):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                """UPDATE Users SET discount = %s WHERE telegram_id=%s""", (discount, telegram_id))
            cursor.fetchone()
            self.connection.commit()
            self.connection.close()

    def update_free_diary_records(self, telegram_id):
        self.connection.ping()
        with self.connection.cursor() as cursor:
            cursor.execute(
                """UPDATE Users SET free_diary_records = free_diary_records - 1 WHERE telegram_id=%s""", (telegram_id))
            cursor.fetchone()
            self.connection.commit()
            self.connection.close()

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
                name = %s,
                weight = %s,
                height = %s,
                age = %s,
                activity= %s, 
                sex= %s, 
                goal= %s
                WHERE telegram_id=%s""", (
                    settings.name,
                    settings.weight,
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
