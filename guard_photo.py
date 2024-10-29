import logging
import json
import base64
from aiogram import Router, types
from aiogram.types import BufferedInputFile

# Initialize router and set logging level to DEBUG for full traceability
photo_router = Router()
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@photo_router.message(
    lambda message: message.web_app_data and json.loads(message.web_app_data.data).get('app_type') == 'photo')
async def handle_photo_data(message: types.Message):
    try:
        logger.debug("Received data from WebApp")
        data = json.loads(message.web_app_data.data)

        # Step 1: Verify app_type is 'photo'
        app_type = data.get('app_type')
        if app_type != 'photo':
            logger.error(f"Unexpected app_type received: {app_type}")
            await message.answer("Ошибка: неверный тип данных (ожидается фото).")
            return

        # Step 2: Check for image data and decode it
        photo_base64 = data.get('image_data_base64')
        if not photo_base64:
            logger.error("No image data found in WebApp data.")
            await message.answer("Ошибка: отсутствуют данные изображения.")
            return

        try:
            # Decode base64-encoded image
            photo_data = base64.b64decode(photo_base64.split(',')[1])
            logger.debug(f"Image decoded successfully, size: {len(photo_data)} bytes")
        except Exception as decode_error:
            logger.error(f"Error decoding base64 image data: {decode_error}")
            await message.answer("Ошибка при декодировании изображения.")
            return

        # Step 3: Create a BufferedInputFile for the image
        try:
            input_file = BufferedInputFile(file=photo_data, filename=f"photo_{message.from_user.id}.jpg")
            logger.debug("BufferedInputFile created successfully.")
        except Exception as file_error:
            logger.error(f"Error creating BufferedInputFile: {file_error}")
            await message.answer("Ошибка при создании файла для отправки изображения.")
            return

        # Step 4: Attempt to send the photo
        try:
            await message.answer_photo(photo=input_file, caption="Фото успешно отправлено.")
            logger.info("Photo successfully sent to the user.")
        except Exception as send_error:
            logger.error(f"Error sending photo to Telegram: {send_error}")
            await message.answer("Ошибка при отправке фото.")
            return

    except ValueError as ve:
        logger.error(f"ValueError encountered: {ve}")
        await message.answer(f"Ошибка: {ve}")
    except Exception as e:
        logger.error("Unhandled error in handle_photo_data", exc_info=True)
        await message.answer("Произошла ошибка при обработке данных.")
