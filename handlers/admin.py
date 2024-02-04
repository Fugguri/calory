from aiogram import types, Bot
from aiogram import Dispatcher, filters
from aiogram.dispatcher.handler import ctx_data
from aiogram.dispatcher import FSMContext

from db import Database
from utils import exel_writer
from config.config import Config
from keyboards.keyboards import Keyboards
from models import Promo
import os


async def admin(message: types.Message):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']
    markup = await kb.admin_kb()

    # if db.get_user(message.from_user.id).role != "ADMIN":
    #     return

    await message.answer("Выберите пункт меню", reply_markup=markup)


async def commands(callback: types.CallbackQuery, state: FSMContext, callback_data: dict):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']

    command = callback_data["command"]
    if command == "mail":
        markup = await kb.mailing_kb("wait_mail_text")
        await state.set_data({"mail_text": '', "mail_photo": ""})
        text = "Введите текст рассылки"
        await state.set_state("wait_mail_text")
    if command == 'statistic':
        markup = await kb.back_kb("admin")
        users = db.get_all_users()
        exel_writer.write_users(users, "docs/users.xlsx")
        await callback.message.answer_document(open("docs/users.xlsx", "rb"))
        os.remove("docs/users.xlsx")
        return
    if command == 'edit promt':
        markup = await kb.back_kb("admin")
        text = "Отправьте новый промт"
        await state.set_state("wait_new_promt")

    if command == 'promo':
        markup = await kb.back_kb("admin")
        text = "Отправьте промокод"
        await state.set_state("wait_promo")
    if command == 'promo_stats':
        markup = await kb.back_kb("admin")
        promos = db.get_all_promo()
        text = "Статистика по промокодам"
        for promo in promos:
            text += "\n-----\n" + promo.__repr__()
    await callback.message.answer(text, reply_markup=markup)
    await callback.message.delete()


async def wait_promo(message: types.Message, state: FSMContext):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']

    markup = await kb.back_kb("admin")
    await state.update_data(promo_code=message.text)
    await message.answer("Сколько процентов будет скидка. Укажите цифрами.", reply_markup=markup)
    await state.set_state("wait_promo_percent")


async def wait_promo_percent(message: types.Message, state: FSMContext):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']

    markup = await kb.back_kb("admin")
    try:
        percent = int(message.text)
    except:
        await message.answer("Введите проценты цифрами", reply_markup=markup)
        return
    promo = await state.get_data()
    promo_code = promo.get("promo_code")
    markup = await kb.confirm_promo_kb(promo_code=promo_code, percent=percent)
    await state.update_data(promo_code_percent=percent)
    await message.answer(f"<b>Подтвердите промокод:</b>\nПРОМОКОД: {promo_code}\nСКИДКА: {percent}%", reply_markup=markup)
    await state.set_state("wait_promo_percent")


async def add_promo(callback: types.CallbackQuery, state: FSMContext, callback_data: dict):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']

    code = callback_data.get("code")
    percent = callback_data.get("percent")

    promo = Promo(code=code, percent=percent)

    db.add_promo(promo)
    await state.finish()
    markup = await kb.admin_kb()
    await callback.message.answer(f"Добавлен промокод:\n"+promo.__repr__(), reply_markup=markup)


async def wait_mail_text(message: types.Message, state: FSMContext):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']

    markup = await kb.mailing_kb("wait_mail_photo")
    await state.update_data(mail_text=message.text)
    await message.answer("Отправьте изображение для рассылки.\nЕсли изображения не будет нажмите кнопку ниже.", reply_markup=markup)
    await state.set_state("wait_mail_photo")
    await message.delete()


async def wait_new_promt(message: types.Message, state: FSMContext):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']

    text = message.text
    await state.finish()
    db.update_promt(text)
    await message.answer("Промт был обновлен.\nНовый промт:\n"+text)


async def wait_mail_photo(message: types.Message, state: FSMContext):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']

    markup = await kb.mailing_kb("wait_mail_photo")
    if message.content_type == types.ContentType.TEXT:
        await message.answer("Получен текст, отправьте изображение!", reply_markup=markup)
        return

    markup = await kb.mailing_kb("wait_mail_photo", True)
    url = message.photo[0].file_id
    await state.update_data(mail_photo=url)

    await state.set_state("wait_mail_photo")
    await message.answer("Получено изображение\nВы можете отправить без изображения.ЧТобы обновить изображение - отправьте новое изображение", reply_markup=markup)


async def mailing(calaback: types.CallbackQuery, state: FSMContext, callback_data: dict):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']
    bot: Bot = ctx_data.get()['bot']

    data = await state.get_data()

    command = callback_data["command"]

    if command == "no_photo":
        text = 'Проверьте текст рассылки и подтвердите рассылку кнопкой ниже.\n\n'
        text += data['mail_text']
        markup = await kb.mailing_kb("confirm")

    if command == "start_with_photo":
        markup = await kb.mailing_kb()
        text = "Начинаю рассылку"
        mes = await calaback.message.answer(text, reply_markup=markup)
        try:
            users = db.get_all_users()
            mail_text = data['mail_text']
            mail_photo = data['mail_photo']
            for user in users:
                await bot.send_photo(chat_id=user.user_id, photo=mail_photo, caption=mail_text)
        except Exception as ex:
            print(ex)
        finally:
            text = "Разослано"
            await mes.delete()

    if command == "start":
        markup = await kb.mailing_kb()
        text = "Начинаю рассылку"
        mes = await calaback.message.answer(text, reply_markup=markup)
        try:
            users = db.get_all_users()
            mail_text = data['mail_text']
            for user in users:
                await bot.send_message(chat_id=user.user_id, text=mail_text)
        except Exception as ex:
            print(ex)
        finally:
            text = "Разослано"
            await mes.delete()

    await calaback.message.answer(text, reply_markup=markup)


def register_admin_handlers(dp: Dispatcher, kb: Keyboards):

    dp.register_message_handler(admin, commands="admin", state="*")
    dp.register_message_handler(wait_mail_text, state="wait_mail_text")
    dp.register_message_handler(wait_new_promt, state="wait_new_promt")
    dp.register_message_handler(wait_promo, state="wait_promo")
    dp.register_message_handler(wait_promo_percent, state="wait_promo_percent")
    dp.register_callback_query_handler(
        mailing, kb.mailing_cd.filter(), state="*")
    dp.register_callback_query_handler(
        add_promo, kb.confirm_promo_cd.filter(), state="*")
    dp.register_callback_query_handler(
        commands, kb.admin_cd.filter(), state="*")
    dp.register_message_handler(wait_mail_photo,
                                content_types=[
                                    types.ContentType.TEXT, types.ContentType.PHOTO],
                                state='wait_mail_photo')
