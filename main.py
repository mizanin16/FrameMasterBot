import logging
import os.path
import sys
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import BufferedInputFile
from io import BytesIO
from PIL import Image
from decouple import config
from aiogram.filters.command import Command
from aiogram import F

BOT_TOKEN = config('BOT_TOKEN')

dp = Dispatcher()


@dp.message(Command('start'))
async def command_start_handler(message: types.Message):
    """
    Этот обработчик реагирует на команду /start
    """
    await message.answer(f"Привет, {message.from_user.full_name}! Отправь мне изображение, и я добавлю на него рамку.")


@dp.message(F.photo)
@dp.message(F.document)
async def process_image(message: types.Message, bot: Bot):
    """
    Обработчик изображений. Добавляет рамку на изображение и отправляет его обратно пользователю.
    """
    # Получение объекта фотографии
    if message.photo:
        photo = message.photo[-1]
    elif message.document:
        file_id = message.document.file_id
        photo = await bot.get_file(file_id)
    else:
        return
    # Получение байтов фотографии без загрузки файла
    photo_bytes = await bot.download(photo)
    if message.caption == 'Заменить рамку':
        path_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'add.PNG')
        await bot.download(photo, path_file)
        await bot.send_message(chat_id=message.chat.id, text='Рамка заменена успешна! Поздравляю!')
        return
    result_image = add_frame(photo_bytes)
    # Отправка измененной фотографии пользователю
    text_file = BufferedInputFile(result_image, filename="file.jpeg")

    await bot.send_photo(chat_id=message.chat.id, photo=text_file)


def add_frame(image):
    main_image = Image.open(image)
    path_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'add.PNG')
    # Загрузка изображения-рамки
    frame_image = Image.open(path_file)

    main_width, main_height = main_image.size

    # Масштабирование рамки до размеров основного изображения
    frame_image = frame_image.resize((main_width, main_height))

    # Накладывание рамки
    main_image.paste(frame_image, (0, 0), frame_image)

    main_image.save("result_image.jpg")

    with BytesIO() as output:
        main_image.save(output, format="JPEG")
        output.seek(0)
        return output.read()


async def main():
    bot = Bot(BOT_TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
