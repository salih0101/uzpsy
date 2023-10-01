from states import Uz_Settings
import sqlite3
import types
import config
from settings import *
import asyncio

bot = Bot(config.TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)


@dp.message_handler(commands=['start'])
async def start_message(message):
    user_id = message.from_user.id
    checker = database.check_user(user_id)

    if checker:
        await message.answer('Приветствуем вас в PsychoFemme \n\nВыберите раздел🔽',
                             reply_markup=uzbtns.uz_main_menu_kb())
    else:
        await message.answer(
            'Приветствую, Пройдите простую регистрацию чтобы в дальнейшем не было проблем!\n\nОтправьте Имя для регистрации!',
            reply_markup=uzbtns.ReplyKeyboardMarkup())
        await UserRegistration.getting_name_state.set()


async def broadcast_message(message_text):
    conn = sqlite3.connect('uzpsycho.db')
    cursor = conn.cursor()

    cursor.execute('SELECT user_id FROM users')
    users = cursor.fetchall()

    for user in users:
        user_id = user[0]
        await bot.send_message(chat_id=user_id, text=message_text)


@dp.message_handler(commands=['broadcast'])
async def broadcast_command(message: types.Message):
    command_args = message.text.split(' ', maxsplit=1)
    if len(command_args) == 2:
        message_text = command_args[1]
        await broadcast_message(message_text)
        await message.reply(f'Сообщение успешно отправлено всем пользователям.')
    else:
        await message.reply('Неверный формат команды. Используйте /broadcast message_text')


@dp.message_handler(state=UserRegistration.getting_name_state)
async def get_name(message, state=UserRegistration.getting_name_state):
    user_answer = message.text

    await state.update_data(name=user_answer)
    await message.answer("Имя сохранил!\n\nОтправьте номер телефона!",
                         reply_markup=uzbtns.uz_phone_number_kb())

    await UserRegistration.getting_phone_number.set()


@dp.message_handler(state=UserRegistration.getting_phone_number, content_types=['text', 'contact'])
async def get_number(message: types.Message, state=UserRegistration.getting_phone_number):
    user_answer = message.text

    if message.content_type == 'text':
        user_answer = message.text

        if not user_answer.replace('+', '').isdigit():
            await message.answer('Отправьте номер телефона')
            return

    elif message.content_type == 'contact':
        user_answer = message.contact.phone_number

    await state.update_data(number=user_answer)
    await message.answer("Номер сохранил! Вы прошли регистрацию\n\nВыберите раздел.",
                         reply_markup=uzbtns.uz_main_menu_kb())

    all_info = await state.get_data()
    user_id = message.from_user.id
    name = all_info.get("name")
    phone_number = all_info.get("number")
    times = all_info.get("time_sub")
    end_subb = all_info.get("end_sub")
    gender = user_answer
    user_status = all_info.get("status")
    price = all_info.get("amount_sub")

    database.add_user(user_id, name, phone_number, times, end_subb, gender, user_status, price)

    await state.finish()


@dp.message_handler(state=Uz_Settings.uz_set_name)
async def change_name_db(message, state=Uz_Settings.uz_set_name):
    user_answer = message.text

    await state.update_data(name=user_answer)

    ch_name = await state.get_data()
    user_id = message.from_user.id
    database.change_name(user_id, ch_name)
    await state.finish()
    await message.answer("Ism muvaffaqiyatli o'zgartirildi",
                         reply_markup=uzbtns.uz_settings_kb())


@dp.message_handler(state=Uz_Settings.uz_set_number)
async def change_number_db(message, state=Uz_Settings.uz_set_number):
    user_answer = message.text

    await state.update_data(phone_number=user_answer)

    ch_number = await state.get_data()
    user_id = message.from_user.id
    database.change_number(user_id, ch_number)
    await state.finish()
    await message.answer("Raqam muvaffaqiyatli o'zgartirildi",
                         reply_markup=uzbtns.uz_settings_kb())


@dp.message_handler(state=Uz_Settings.uz_set_setting, content_types=["text"])
async def set_name(message):
    user_answer = message.text
    user_id = message.from_user.id

    if user_answer == "Ismni o'zgartirish":
        await message.answer("Ism yuboring")
        await Uz_Settings.uz_set_name.set()

    elif user_answer == "Raqamni o'zgartirish":
        await message.answer("Telefon raqam yuboring")
        await Uz_Settings.uz_set_number.set()

    elif user_answer == 'Ortgа qaytish':
        await message.answer("Siz 'Sozlamalar' menusidasiz",
                             reply_markup=uzbtns.uz_settings_kb())
        await dp.current_state(user=user_id).finish()


# Обработчик основного меню
@dp.message_handler(content_types=["text"])
async def main_menu(message):
    user_id = message.from_user.id
    user_answer = message.text
    photo_path = 'List_of_courses/course_photo.png'

    if user_answer == "📝Kurs uchun to'lov":
        await message.answer("Kurs uchun to'lovni amalga oshirish uchun 'To'lov 💳💰 tugmasini bosing'",
                             reply_markup=uzcourse.uz_pay_inline())

    elif user_answer == "📚Kurslar":
        await message.answer("Kursni tanlang!",
                             reply_markup=uzcourse.uz_list_courses())

    elif user_answer == "⚙️Sozlamalar":
        await message.answer("Siz '⚙️Sozlamalar' bo'limidasiz",
                             reply_markup=uzbtns.uz_settings_kb())

    elif user_answer == "👤Profil":
        await message.answer("Bo'limni tanlang",
                             reply_markup=uzbtns.uz_change_data_kb())
        await states.Uz_Settings.uz_set_setting.set()

    elif user_answer == '🌟"Yangi Men" kursi':
        await bot.send_photo(photo=open(photo_path, 'rb'), chat_id=user_id, caption=welcome_msg_uz,
                             reply_markup=uzcourse.uz_some_kb())

    elif user_answer == '🌟"Men ayolman" kursi':

        await message.answer('Мен аелман\n\n'
                             'Курс вактинчалик тухтатилган\n\n'
                             'Болаликдаги травмалар\n'
                             'Онг ости блоклари билан,\n'
                             'Установкалар билан,\n'
                             'Ота она муносабатлари,\n'
                             'Турмуш урток муносабати, хиенат мавзулари илдизи билан ишланади\n')

    elif user_answer == '🌟"Ruhiy rivojlanish" kursi':

        await message.answer('Рухий ривожланиш\n\n'
                             'Курс вактинчалик тухтатилган\n\n'
                             'Калб хотиржамлиги эришиш\n'
                             'Калб касалликларидан халос булиш\n'
                             'Калб касбини топиш\n'
                             'Ичингиздаги яратувчи билан уланиш\n')


    elif user_answer == "Ortga qaytishh":
        await message.answer("Siz 'Asosiy menu'ga o'tdingiz",
                             reply_markup=uzbtns.uz_main_menu_kb())
        await dp.current_state(user=user_id).finish()

    elif user_answer == "Ortgа qaytish":
        await message.answer("Вы вернулись в ГЛАВНОЕ МЕНЮ",
                             reply_markup=uzbtns.uz_main_menu_kb())
        await dp.current_state(user=user_id).finish()

    elif user_answer == "Ortga qаytish":
        await message.answer("Вы вернулись в ГЛАВНОЕ МЕНЮ",
                             reply_markup=uzbtns.uz_main_menu_kb())
        await dp.current_state(user=user_id).finish()

    elif user_answer == "Ortga qaytish":
        await message.answer("Вы вернулись в ГЛАВНОЕ МЕНЮ",
                             reply_markup=uzbtns.uz_main_menu_kb())
        await dp.current_state(user=user_id).finish()


# Обработчик курса "Новая Я"
@dp.callback_query_handler(lambda query: True)
async def course_fivedays(call: types.CallbackQuery):
    user_id = call.from_user.id

    if call.data == "uz_start":

        status = 1
        database.set_status(user_id, status)

        # Отправляем действие "печатание" перед отправкой изображения и приветственного сообщения
        await bot.send_chat_action(chat_id=user_id, action=types.ChatActions.TYPING)
        await bot.answer_callback_query(call.id)

        await bot.send_chat_action(chat_id=user_id, action=types.ChatActions.TYPING)
        await asyncio.sleep(0.5)
        await bot.send_message(call.from_user.id, text_uz, reply_markup=uzbtns.ReplyKeyboardRemove())

        await bot.send_chat_action(chat_id=user_id, action=types.ChatActions.TYPING)
        await asyncio.sleep(3)
        await bot.send_message(call.from_user.id, text2_uz,
                               reply_markup=uzcourse.uz_info_course())

        admin_id = 5928000362  # Замените на айди администратора
        await bot.send_message(admin_id, f"Пользователь {call.from_user.first_name} начал курс")


    # При нажатии кнопку Продолжить
    elif call.data == "uz_next":

        # await bot.delete_message(call.message.chat.id, call.message.message_id)
        current_status = database.get_status(user_id)

        if current_status == 1:

            await bot.send_chat_action(chat_id=user_id, action=types.ChatActions.TYPING)
            await asyncio.sleep(3)

            await bot.send_message(call.from_user.id, "1-kun videosini ochish uchun. Quyidagi tugmani bosing. 👇\n\n",
                                   reply_markup=uzcourse.uz_get_youtube())

            await bot.send_chat_action(chat_id=user_id, action=types.ChatActions.TYPING)
            await asyncio.sleep(3)
            await bot.send_message(call.from_user.id, day_one_uz)

            await bot.send_chat_action(chat_id=user_id, action=types.ChatActions.TYPING)
            await asyncio.sleep(3)
            await bot.send_message(call.from_user.id, emotions_text_uz,
                                   reply_markup=uz_inline_buttons.uz_emotions_day_two())

        else:
            await bot.send_message(call.from_user.id, "Kurs hali tugamagan. Kursni davom ettirmoqchimisiz? 📚💡",
                                   reply_markup=uzcourse.uz_day_two_yes())

    # Переход на Второй день
    if call.data == 'uz_emotions_day_two' or call.data == 'uz_emotions_day_two1' or call.data == 'uz_day_two_yes':

        await bot.answer_callback_query(call.id)
        await bot.send_message(call.from_user.id,
                               "Siz kursning ikkinchi kuniga o'tdingiz. 🌟\nSizga tez orada yangi xabar yuboriladi! 🚀")
        await bot.delete_message(call.message.chat.id, call.message.message_id)

        # Ожидание 24 часа
        await asyncio.sleep(86400)
        database.update_status(user_id)

        await asyncio.sleep(2)
        current_status = database.get_status(user_id)

        if current_status == 2:
            await asyncio.sleep(5)

            await bot.send_message(call.from_user.id, day_two_notif_uz, reply_markup=uzcourse.uz_send_audio())

            await bot.send_chat_action(chat_id=user_id, action=types.ChatActions.TYPING)
            await asyncio.sleep(2)


    elif call.data == 'uz_send_audio':
        current_status = database.get_status(user_id)

        if current_status == 2:
            audio_path = 'List_of_courses/1.ogg'
            audio_path2 = 'List_of_courses/2.ogg'

            if os.path.exists(audio_path) and os.path.exists(audio_path2):
                with open(audio_path, 'rb') as audio_file:
                    await bot.send_chat_action(chat_id=user_id, action=types.ChatActions.UPLOAD_AUDIO)
                    await bot.send_audio(call.from_user.id,
                                         audio_file,
                                         caption="Kunning mavzusi bo'yicha audio")
            await bot.answer_callback_query(call.id)
            await bot.send_chat_action(chat_id=user_id, action=types.ChatActions.TYPING)
            await asyncio.sleep(3)
            await bot.send_message(call.from_user.id, 'Ikkinchi kunning audiosini ochish uchun. Tugmani bosing. 👇',
                                   reply_markup=uz_inline_buttons.uz_send_task())

    # Задание второго дня
    elif call.data == 'uz_send_task1':

        audio_path2 = 'List_of_courses/2.ogg'

        if os.path.exists(audio_path2) and os.path.exists(audio_path2):

            with open(audio_path2, 'rb') as audio_file4:

                await bot.answer_callback_query(call.id)
                await bot.send_chat_action(chat_id=user_id, action=types.ChatActions.UPLOAD_AUDIO)
                await asyncio.sleep(3)
                await bot.send_audio(call.from_user.id, audio_file4,
                                     caption='Kunning vazifasi')
                await asyncio.sleep(3)
                await bot.send_message(call.from_user.id, emotions_text_uz,
                                       reply_markup=uz_inline_buttons.uz_emotions_day_three())

        else:
            await bot.send_message(call.from_user.id, "Kurs hali tugamagan. Iltimos, oldingi kunlarni yakunlang. 🔒📚")
            await asyncio.sleep(0.5)
            await bot.send_message(call.from_user.id,
                                   "Kurs hali tugamagan. Agar siz oldingi kunni tugatgan bo'lsangiz, tugmani bosing 👉🎯",
                                   reply_markup=uz_inline_buttons.uz_day_three_yes())

    # Переход на Третий день
    if (call.data == 'uz_emotions_day_three' or
            call.data == 'uz_emotions_day_three1' or call.data == 'uz_day_three_yes'):

        await bot.send_message(call.from_user.id,
                               "Siz kursning uchinchi kuniga o'tdingiz. 🎉📚\nSizga tez orada yangi xabar yuboriladi! 🚀")
        await bot.delete_message(call.message.chat.id, call.message.message_id)

        # Ожидание 24 часа
        await asyncio.sleep(86400)
        database.update_status(user_id)

        await asyncio.sleep(2)
        current_status = database.get_status(user_id)

        if current_status == 3:
            await asyncio.sleep(5)
            await bot.send_chat_action(chat_id=user_id, action=types.ChatActions.TYPING)
            await bot.send_message(call.from_user.id, day_three_notif_uz,
                                   reply_markup=uz_inline_buttons.uz_day_three_video())

            await asyncio.sleep(3)
            await bot.send_message(call.from_user.id, day_three_message_uz,
                                   reply_markup=uz_inline_buttons.uz_day_three_ok())


    # ---Если нажал "Готова"---
    elif call.data == 'uz_yes':

        await bot.send_chat_action(chat_id=user_id, action=types.ChatActions.TYPING)
        await asyncio.sleep(3)
        await bot.send_message(call.from_user.id, day_three_yes_message_uz)
        await bot.send_chat_action(chat_id=user_id, action=types.ChatActions.TYPING)
        await asyncio.sleep(3)
        await bot.send_message(call.from_user.id,
                               'Endi Psixologdan vazifa. 💡💭\n\nVazifani ochish uchun, tugmani bosing 👉📝',
                               reply_markup=uz_inline_buttons.uz_get_task_three())


    # ---Отправка задание к третьему дню---
    elif call.data == 'uz_send_task3':
        await bot.send_chat_action(chat_id=user_id, action=types.ChatActions.TYPING)
        await asyncio.sleep(3)
        await bot.send_message(call.from_user.id, day_three_task_uz)
        await bot.send_chat_action(chat_id=user_id, action=types.ChatActions.TYPING)
        await asyncio.sleep(3)
        await bot.send_message(call.from_user.id, emotions_text_uz,
                               reply_markup=uz_inline_buttons.uz_emotions_day_four())


    elif call.data == 'uz_emotions_day_four' or call.data == 'uz_emotions_day_four1' or call.data == 'uz_day_four_yes':

        await bot.delete_message(call.message.chat.id, call.message.message_id)

        await bot.send_chat_action(chat_id=user_id, action=types.ChatActions.TYPING)
        await asyncio.sleep(2)
        await bot.send_message(call.from_user.id,
                               "Siz kursning to'rtinchi kuniga o'tdingiz!!!\nTez orada sizga habar yuboriladi! 🚀 🎓")

        # Ожидание 24 часа
        await asyncio.sleep(86400)
        database.update_status(user_id)

        await asyncio.sleep(2)
        current_status = database.get_status(user_id)

        if current_status == 4:

            await bot.send_chat_action(chat_id=user_id, action=types.ChatActions.TYPING)
            await asyncio.sleep(3)
            await bot.send_message(call.from_user.id, day_four_notif_uz)

            audio_path2 = 'List_of_courses/day_four.ogg'

            if os.path.exists(audio_path2) and os.path.exists(audio_path2):
                with open(audio_path2, 'rb') as audio_file4:

                    await asyncio.sleep(0.5)

                    await bot.send_chat_action(chat_id=user_id, action=types.ChatActions.UPLOAD_AUDIO)
                    await bot.send_audio(call.from_user.id, audio_file4,
                                         reply_markup=uz_inline_buttons.uz_get_task_four())

            else:
                await bot.send_message(call.from_user.id,
                                       "Kurs hali tugamagan. Agar siz oldingi 3 kunni tugatgan bo'lsangiz, tugmani bosing 👉",
                                       reply_markup=uz_inline_buttons.uz_day_five_yes())


    elif call.data == 'uz_send_task4':

        await bot.send_chat_action(chat_id=user_id, action=types.ChatActions.TYPING)
        await asyncio.sleep(3)
        await bot.send_message(call.from_user.id, day_four_task_uz)
        await asyncio.sleep(3)
        await bot.send_message(call.from_user.id, emotions_text_uz,
                               reply_markup=uz_inline_buttons.uz_emotions_day_five())

    # ---Пятый день---
    elif call.data == 'uz_emotions_day_five' or call.data == 'uz_emotions_day_five1' or call.data == 'uz_day_five_yes':

        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await bot.send_message(call.from_user.id,
                               "Siz kursning beshinchi kuniga o'tdingiz. 🌟📚\nTez orada sizga habar yuboriladi! 🚀")
        # Ожидание 24 часа
        await asyncio.sleep(86400)
        database.update_status(user_id)

        await asyncio.sleep(2)
        current_status = database.get_status(user_id)

        if current_status == 5:
            await asyncio.sleep(3)
            await bot.send_chat_action(chat_id=user_id, action=types.ChatActions.TYPING)
            await bot.send_message(call.from_user.id, day_five_notif_uz)

            await bot.send_chat_action(chat_id=user_id, action=types.ChatActions.UPLOAD_VIDEO)
            await asyncio.sleep(3)
            await bot.send_message(call.from_user.id, "Videoni ko'rish uchun tugmani bosing 🎥👇",
                                   reply_markup=uz_inline_buttons.uz_day_five_video())

            await bot.send_chat_action(chat_id=user_id, action=types.ChatActions.TYPING)
            await asyncio.sleep(3)
            await bot.send_message(call.from_user.id, day_five_text_uz)
            await asyncio.sleep(5)
            await bot.send_message(call.from_user.id, discount_text_uz)


    # ---Если нажал "Не готова"---
    elif call.data == 'uz_no':
        await bot.send_chat_action(chat_id=user_id, action=types.ChatActions.TYPING)
        await asyncio.sleep(3)
        await bot.send_message(call.from_user.id, day_three_no_message_uz)
        await bot.send_chat_action(chat_id=user_id, action=types.ChatActions.TYPING)
        await asyncio.sleep(3)
        await bot.send_message(call.from_user.id, discount_text_uz)


# https://www.youtube.com/channel/UCY9jGnDyqNCUUktm2ry-SFw

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
