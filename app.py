from flask import Flask
from flask_login import LoginManager
from models import db, clear_database
import logging
import colorlog
import os

def init_log():
    # 檢查並創建日誌目錄
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 設定日誌紀錄器
    log_file = os.path.join(log_dir, 'app.log')
    logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # 創建輸出至檔案的處理器
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)

    # 創建輸出至控制台的處理器
    console_handler = logging.StreamHandler()  # 創建輸出至控制台的處理器
    console_handler.setLevel(logging.INFO)

    # 設定格式
    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # 將處理器添加到日誌紀錄器中
    logger = logging.getLogger('app_log')
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

def create_app():
    app = Flask(__name__)

    db.create_all()

    app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return db.query(User).get(int(user_id))

    # blueprint for auth routes in our app
    from auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    app.run(debug=True)


if __name__ == '__main__':
    # clear_database()
    init_log()
    create_app()
