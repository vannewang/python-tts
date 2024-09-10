import tkinter as tk
import threading
from flask import Flask, request, jsonify, send_from_directory, url_for
import pyttsx3
from pydub import AudioSegment
import os
import tempfile

app = Flask(__name__)

AudioSegment.converter = r"C:\Program Files\ffmpeg6.1\bin\ffmpeg.exe"
# 配置项
CUSTOM_TEMP_DIR = r'D:\atts'


def initialize_tts_engine():
    return pyttsx3.init()


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


def start_flask_app():
    app.run(host='0.0.0.0', port=19000, debug=False, use_reloader=False)


def on_start_button_click():
    global app_debug_var  # 声明 app_debug_var 为全局变量
    if not app_debug_var:
        threading.Thread(target=start_flask_app).start()
        button_start.config(state=tk.DISABLED)
        label_status.config(text="服务已启动")
        app_debug_var = True


@app.route('/tts', methods=['POST'])
def text_to_speech():
    data = request.json
    text = data.get('text', '')

    temp_files = []
    try:
        # 确保目录存在
        if not os.path.exists(CUSTOM_TEMP_DIR):
            os.makedirs(CUSTOM_TEMP_DIR)

        # 生成临时文件路径
        with tempfile.NamedTemporaryFile(suffix='.wav', dir=CUSTOM_TEMP_DIR, delete=False) as temp_wav_file:
            temp_wav_path = temp_wav_file.name
            temp_files.append(temp_wav_path)

        # 将文本转换为语音并保存为 WAV 文件
        save_text_to_wav(text, temp_wav_path)

        with tempfile.NamedTemporaryFile(suffix='.mp3', dir=CUSTOM_TEMP_DIR, delete=False) as temp_mp3_file:
            temp_mp3_path = temp_mp3_file.name

        # 使用 pydub 将 WAV 文件转换为 MP3 文件
        convert_wav_to_mp3(temp_wav_path, temp_mp3_path)

        file_url = url_for('files', filename=os.path.basename(temp_mp3_path))

        # 返回 MP3 文件的路径
        return jsonify({'mp3_path': file_url}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # 清理生成的临时文件
        clean_up(temp_files)


@app.route('/files/<path:filename>')
def files(filename):
    return send_from_directory(CUSTOM_TEMP_DIR, filename)


# 创建 GUI
root = tk.Tk()
root.title("TTS文字转语音")
# 设置窗口的宽度和高度
window_width = 280
window_height = 160
root.geometry(f"{window_width}x{window_height}")
# 创建启动按钮
button_start = tk.Button(root, text="启动服务", command=on_start_button_click)
button_start.pack(pady=30)

# 创建状态标签
label_status = tk.Label(root, text="服务未启动")
label_status.pack(pady=15)

# 全局变量，用于跟踪 Flask 应用程序是否已经在运行
app_debug_var = False

# 运行 GUI 主循环
root.mainloop()


def start():
    threading.Thread(target=start_flask_app).start()


if __name__ == '__main__':
    start()
