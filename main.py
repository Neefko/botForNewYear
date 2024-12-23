from aiogram.filters.command import Command as command
from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardBuilder
from aiogram import Bot, Dispatcher, F, types
from aiogram.exceptions import TelegramAPIError
from aiogram.types import FSInputFile
import random
import os
import asyncio
import words
from get_from_db import DatabaseBot
from santa_link import Link
import generate
# from bs4 import BeautifulSoup
# from selenium import webdriver
# import time

# Тут должен быть ваш токен. Ссылка на бота https://t.me/new_33_year_bot
token = Bot(token="8191555772:AAGejXO9FhE9NCuzx65hphPOHQgYy8lpaIM")
dp = Dispatcher()

db_link = Link()
db = DatabaseBot()

def play_callback_filter(callback: types.CallbackQuery) -> bool:
    return callback.data.startswith("play_")

def language(user_id):
    result = db.get_language(user_id)
    if result:
        return int(result[0])
    return 0


@dp.message(command("start"))
async def start(message: types.Message):
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    if args:
        unique_id = args[0]
        user_id = message.from_user.id

        db_link.add_participants(unique_id, user_id)
        participants = db_link.get_participants(unique_id)
        await message.answer(words.reg_success[language(message.from_user.id)] + str(len(participants)))
    else:
        if db.get_user(message.from_user.id):
            await message.answer(words.reg[language(message.from_user.id)])
        else:
            builder = InlineKeyboardBuilder()
            builder.row(
                types.InlineKeyboardButton(text="Русский", callback_data="ru"),
                types.InlineKeyboardButton(text="English", callback_data="en")
            )
            await message.answer("Давай выберем язык который тебе удобен, English or Spanish? Шучу, предпочитаешь English или Русский?", reply_markup=builder.as_markup())


@dp.callback_query(F.data.startswith("en"))
async def english_language(call: types.CallbackQuery):
    language = 1
    await call.answer("English language is set")
    if db.exam_id(call.from_user.id) is False:
        db.register(call.from_user.id, call.from_user.username, language)
    else:
        db.update_language(call.from_user.id, language)
    await call.message.delete()


@dp.callback_query(F.data.startswith("ru"))
async def russian_language(call: types.CallbackQuery):
    language = 0
    await call.answer("Установлен русский язык")
    if db.exam_id(call.from_user.id) is False:
        db.register(call.from_user.id, call.from_user.username, language)
    else:
        db.update_language(call.from_user.id, language)
    await call.message.delete()


@dp.message(command("language"))
async def edit_language(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="Русский", callback_data="ru"),
        types.InlineKeyboardButton(text="English", callback_data="en")
    )
    await message.answer(words.languages[language(message.from_user.id)], reply_markup=builder.as_markup())

@dp.message(command("info"))
async def info(message: types.Message):
    await message.answer(words.info[language(message.from_user.id)])


@dp.message(command("santa"))
async def santa(message: types.Message):
    bot_username = (await token.get_me()).username
    unique_id, link = db_link.generate_unique_link(bot_username)
    db_link.save_game(unique_id, message.from_user.id)
    await message.answer(words.santa[language(message.from_user.id)] +  link)


@dp.message(command("santa_status"))
async def santa_status(message: types.Message):
    games = db_link.info_santa_participants(message.from_user.id)
    if not games:
        await message.answer(words.santa_status_0[language(message.from_user.id)])
    else:
        await message.answer(words.santa_status_1[language(message.from_user.id)])
        for game in games:
            game_id = game["id"]
            participants = game["participants"]
            participant_names = []
            for participant_id in participants:
                name = db.get_name(participant_id)
                if name:
                    participant_names.append(name)
                else:
                    participant_names.append(words.santa_status_2[language(message.from_user.id)] + participant_id)
            if participant_names:
                participant_list = "\n".join(participant_names)
            else:
                participant_list = words.santa_status_3[language(message.from_user.id)]
            await message.answer(words.santa_status_4[language(message.from_user.id)], game_id + "\n", words.users[language(message.from_user.id)] + "\n", participant_list)


@dp.message(command("santa_play"))
async def santa_play(message: types.Message):
    games = db_link.info_santa_participants(message.from_user.id)
    if not games:
        await message.answer(words.santa_play_0[language(message.from_user.id)])
        return
    builder = InlineKeyboardBuilder()
    for game in games:
        game_id = game["id"]
        builder.add(InlineKeyboardButton(text=game_id, callback_data=f"play_{game_id}"))
    await message.answer(words.santa_play_1[language(message.from_user.id)], reply_markup=builder.as_markup())

@dp.callback_query(play_callback_filter)
async def handle_play_callback(call: types.CallbackQuery):
    game_id = call.data.split("_", 1)[1]
    try:
        await call.message.answer(words.santa_play_2[language(call.from_user.id)] + " " + game_id)
    except TelegramAPIError as e:
        await call.message.answer(words.error1[language(call.from_user.id)])
        return
    games = db_link.info_santa_participants(call.from_user.id)
    game = None
    pairs = []
    for g in games:
        if g['id'] == game_id:
            game = g
            break
    if not game:
        await call.message.answer(words.santa_play_0[language(call.from_user.id)])
        return
    participants = game['participants']
    random.shuffle(participants)
    if len(participants) < 2:
        await call.message.answer(words.no_users[language(call.from_user.id)])
        return
    for i in range(len(participants)):
        giver_id = participants[i]
        receiver_id = participants[(i + 1) % len(participants)]
        giver_name = db.get_name(giver_id)
        receiver_name = db.get_name(receiver_id)
        pairs.append(f"{giver_name} -> {receiver_name}")
        try:
            await call.bot.send_message(giver_id, words.santa_play_3[language(call.from_user.id)] + " " + receiver_name + "!")
        except TelegramAPIError as e:
            if "business connection not found" in str(e):
                await call.message.answer(
                    words.error2[language(call.from_user.id)] + giver_name + words.error3[language(call.from_user.id)] + giver_name)
                return
            else:
                await call.message.answer(words.error2[language(call.from_user.id)] + giver_name)
    await call.message.answer("\n".join(pairs))

@dp.message(command("postcard"))
async def postcard(message: types.Message):
    await message.answer(words.name[language(message.from_user.id)])
    await message.answer("Введите ваше имя:")
    @dp.message()
    async def name(messag: types.Message):
        user_name = messag.text
        i = generate.postcard(user_name)
        input_file = FSInputFile("test/postcard.jpg")
        await messag.answer_photo(input_file)
        try:
            os.remove("test/postcard.jpg")
        except PermissionError:
            pass


# @dp.message(command("postcard_add"))
# async def postcard_add(message: types.Message):
#     photos = message.photo
#     for photo in photos:
#         await photo.download()
#         photo.save("add/")
#         await message.answer("Successfully added!")


@dp.message(command("discount"))
async def discount(message: types.Message):
    await message.answer(words.discount[language(message.from_user.id)])
    # url = 'https://vk.com/podslushanokovrov1'
    # driver = webdriver.Chrome()
    # driver.get(url)
    # time.sleep(5)
    # soup = BeautifulSoup(driver.page_source, 'html.parser')
    # post_blocks = soup.find_all('div', {'class': 'wall_post_text'})
    # for index, post in enumerate(post_blocks[:10], start=1):
    #     text_inside_block = post.get_text().strip()
    #     await message.answer(f'Пост {index}:\n{text_inside_block}\n')
    # driver.quit()


async def main():
    await dp.start_polling(token)


if __name__ == "__main__":
    asyncio.run(main())