# main.py

from flask import Blueprint, render_template, request
from flask_login import login_required, current_user

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')

@main.route('/upload')
@login_required
def upload():
    return render_template('upload.html')

@main.route('/upload', methods=['GET', 'POST'])
def upload_file():
    uploading = False
    success_message = None
    
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            print(file.filename)
            
            if file.filename != '':
                # 在這裡處理文件，比如保存到伺服器上或執行其他操作
                # 你可以使用 file.save() 或其他相關函數
                # 這裡僅示範顯示文件名稱
                filename = file.filename
                success_message = f"文件上傳成功，文件名稱：{filename}"
                uploading = True

    return render_template('index.html', uploading=uploading, success_message=success_message)



@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name, mail=current_user.email)
