import logging
import logging.handlers
import os
from datetime import datetime

def setup_logger():
    # 日志文件路径
    log_dir = r'D:\atts\log'
    # 日志文件名模板，包含日期
    log_file_name_template = 'httptts_{}.log'.format(datetime.now().strftime('%Y%m%d'))
    full_log_path = os.path.join(log_dir, log_file_name_template)

    # 确保日志目录存在
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 创建一个日志记录器
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # 设置日志级别

    # 创建一个TimedRotatingFileHandler
    handler = logging.handlers.TimedRotatingFileHandler(
        full_log_path, when='midnight', interval=1, backupCount=30, encoding='utf-8'
    )
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # 添加处理器到日志记录器
    logger.addHandler(handler)

    return logger