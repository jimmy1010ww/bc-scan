# main.py

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
import logging
import os
import subprocess
from datetime import datetime, date

main = Blueprint('main', __name__)
UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'

logger = logging.getLogger('app_log')

current_result_id = -1

scan_results = [
]

empty_scan_result = {
    "id": 0,
    "task_status": "pending",
    "task_filename": "None",
    "task_name": "None",
    "task_type": "None",
    "task_date": "None",
    "task_duration_time": "None",
    "task_result": "None"
}

def exec_wana(filename):
    # 執行指令：python3 WANA/wana.py -t 20 -e contract.wasm
    
    command = ['python3', 'WANA/wana.py', '-o', 'result.txt', '-e', filename]
    try:
        subprocess.run(command, check=True)
        result = "Command executed successfully."
        # logger.info("Command executed successfully.")
    except subprocess.CalledProcessError as e:
        result = "Error executing command: {}".format(e)
        # logger.error("Error executing command: {}".format(e))

    return result

@main.route('/')
def index():
    return render_template("index.html")

@main.route('/upload')
@login_required
def upload():
    return render_template("upload.html")

@main.route('/upload', methods=['POST'])
@login_required
def upload_file():
    global current_result_id
    # 從登入狀態中取得使用者名稱
    username = current_user.name    
    logger.info("username: %s" % username)

    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            task_name = request.form.get('task_name')
            contract_category = request.form.get('contract_category')
                 

            # 確認是否有上傳檔案              
            if file.filename != '':
                uploading = True  # 開始上傳
                    
                filename = os.path.join(UPLOAD_FOLDER, username, file.filename)
                file.save(filename)
                logger.info("received file upload.")
                logger.info("file name %s" % filename)
                
                now = datetime.now()

                scan_results.append(
                    {
                        "id": str(current_result_id),
                        "task_status": "pending",
                        "task_filename": file.filename,
                        "task_name": task_name,
                        "task_type": contract_category,
                        "task_date": now.strftime("%d/%m/%Y %H:%M:%S"),
                        "task_duration_time": "Under Estimate",
                        "task_result": "None"
                    }
                )
                
                logger.info("id: %s" % current_result_id)
                logger.info("task_status: %s" % scan_results[0]["task_status"])
                logger.info("task_filename: %s" % scan_results[0]["task_filename"])
                logger.info("task_name: %s" % scan_results[0]["task_name"])
                logger.info("task_type: %s" % scan_results[0]["task_type"])
                logger.info("task_date: %s" % scan_results[0]["task_date"])
                
                
                current_result_id += 1
                
                scan_results[0]["task_status"] = "running"
                
                exec_wana(filename) 
                                
                logger.info("task_result: %s" % scan_results[0]["task_result"])
                logger.info("task_duration_time: %s" % scan_results[0]["task_duration_time"])
        else:
            print("no file")
                
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name, mail=current_user.email)

@main.route('/task')
@login_required
def task():
    logger.info(current_result_id)
    if current_result_id != -1:
        return render_template('task.html', task=scan_results[0], task_result=scan_results, scan_result=render_template("scan_result.html", task=scan_results[0], streamed=True))
    else:
        # 回傳空的 Empty Task List
        return render_template('task.html', task=empty_scan_result, task_result=[empty_scan_result], scan_result=render_template("empty_scan_result.html", task=None, streamed=True))

@main.route("/scan/<scan_id>")
@login_required
def scan_result(scan_id):
    scan = None
    # 避免使用者直接輸入 點選 None 的連結
    if int(scan_id) == 0 and current_result_id == -1:
        return render_template('task.html', task=empty_scan_result, task_result=[empty_scan_result], scan_result=render_template("empty_scan_result.html", task=None, streamed=True))
    else:
        return render_template("task.html", task=scan_results[0], task_result=scan_results, scan_result=render_template("scan_result.html", task=scan_results[int(scan_id)], streamed=True))
    
@main.route('/get_task_num', methods=['GET'])
@login_required
def get_task_num():
    try:
        data = {
            "value": len(scan_results)
        }
    except:
        data = {
            "value": 0
        }
    
    return jsonify(data)