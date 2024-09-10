import threading
from flask import Flask, request, jsonify, send_from_directory, url_for
import pyttsx3
from pydub import AudioSegment
import os
import tempfile
import datetime
from log_config import setup_logger

app = Flask(__name__)
# 配置项
AudioSegment.converter = r"C:\Program Files\ffmpeg6.1\bin\ffmpeg.exe"
CUSTOM_TEMP_DIR = r'D:\atts'
HOST = '0.0.0.0'
PORT = 19000
# 设置日志记录器
logger = setup_logger()


def initialize_tts_engine():
    return pyttsx3.init()


def get_daily_temp_dir():
    # 获取当天的日期并创建文件夹路径
    today = datetime.date.today()
    daily_temp_dir = os.path.join(CUSTOM_TEMP_DIR, today.strftime('%Y-%m-%d'))
    if not os.path.exists(daily_temp_dir):
        os.makedirs(daily_temp_dir)
    return daily_temp_dir, today


def save_text_to_wav(text, temp_wav_path):
    engine = initialize_tts_engine()
    engine.save_to_file(text, temp_wav_path)
    engine.runAndWait()


def convert_wav_to_mp3(temp_wav_path, temp_mp3_path):
    audio = AudioSegment.from_wav(temp_wav_path)
    audio.export(temp_mp3_path, format="mp3")


def clean_up(temp_files):
    for temp_file in temp_files:
        try:
            os.remove(temp_file)
        except OSError as e:
            app.logger.error(f"Error deleting temp file {temp_file}: {e}")
            logger.info(f"删除文件失败 {temp_file}: {e}")


@app.route('/tts', methods=['POST'])
def text_to_speech():
    data = request.json
    text = data.get('text', '')
    logger.info(f"TTS文本转语音内容： {text}")
    temp_files = []
    try:
        # 获取当天的临时文件夹
        daily_temp_dir, today = get_daily_temp_dir()

        # 生成临时文件路径
        with tempfile.NamedTemporaryFile(suffix='.wav', dir=daily_temp_dir, delete=False) as temp_wav_file:
            temp_wav_path = temp_wav_file.name
            temp_files.append(temp_wav_path)

        # 将文本转换为语音并保存为 WAV 文件
        save_text_to_wav(text, temp_wav_path)

        with tempfile.NamedTemporaryFile(suffix='.mp3', dir=daily_temp_dir, delete=False) as temp_mp3_file:
            temp_mp3_path = temp_mp3_file.name

        # 使用 pydub 将 WAV 文件转换为 MP3 文件
        convert_wav_to_mp3(temp_wav_path, temp_mp3_path)

        file_url = url_for('files', filename=f"{today.strftime('%Y-%m-%d')}/{os.path.basename(temp_mp3_path)}",
                           _external=True)
        # 返回 MP3 文件的路径
        return jsonify({'path': file_url}), 200

    except Exception as e:
        logger.error(f"TTS文本转语音失败： {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        # 清理生成的临时文件
        clean_up(temp_files)


@app.route('/files/<path:filename>')
def files(filename):
    return send_from_directory(CUSTOM_TEMP_DIR, filename)


def start_flask_app():
    app.run(host=HOST, port=PORT, debug=False, use_reloader=False)


def start():
    threading.Thread(target=start_flask_app).start()


if __name__ == '__main__':
    start()
