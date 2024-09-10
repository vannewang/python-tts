import pyttsx3
from pydub import AudioSegment

AudioSegment.converter = r"C:\Program Files\ffmpeg6.1\bin\ffmpeg.exe"

# 初始化 TTS 引擎
engine = pyttsx3.init()

# 设置要转换的文本
text = "欢迎陕ZH8989入场"

# 将文本转换为语音并保存为 WAV 文件
engine.save_to_file(text, 'output.wav')
engine.runAndWait()  # 等待语音合成完成

# 使用 pydub 将 WAV 文件转换为 MP3 文件
audio = AudioSegment.from_wav("output.wav")
audio.export("output.mp3", format="mp3")

# 打印完成消息
print("语音合成完成，MP3 文件已保存。")

# 清理生成的 WAV 文件
import os
os.remove('output.wav')