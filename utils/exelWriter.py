import pandas as pd
from models import User


class ExcelWriter:
    def write_users(self, users: list[User], filename: str):
        data = []

        for user in users:
            data.append(user.__dict__)

        df = pd.DataFrame(data)
        df.to_excel(filename, index=False)
