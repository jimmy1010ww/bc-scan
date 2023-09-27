# main.py

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
import logging
import os
import subprocess
from datetime import datetime, date
import pickle
from multiprocessing import Process

main = Blueprint('main', __name__)
UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'

logger = logging.getLogger('app_log')

current_result_id = -1


scan_results = []
with open('scan_results_list.pickle', 'wb') as file:
    pickle.dump(scan_results, file)

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

def update_scan_results():
    global scan_results
    with open('scan_results_list.pickle', 'rb') as file:
        scan_results = pickle.load(file)

def create_task(id, task_status, task_name, task_type, task_filename, task_date, task_duration_time, task_result, wasm_filepath, output_filepath):
    
    scan_results.append(
        {
            "id": str(id),
            "task_status": task_status,
            "task_filename": task_filename,
            "task_name": task_name,
            "task_type": task_type,
            "task_date": task_date,
            "task_duration_time": task_duration_time,
            "task_result": task_result
        }
    )
    
    with open('scan_results_list.pickle', 'wb') as file:
        pickle.dump(scan_results, file)
    
    
    logger.info("id: %s" % id)
    logger.info("task_status: %s" % scan_results[id]["task_status"])
    logger.info("task_filename: %s" % scan_results[id]["task_filename"])
    logger.info("task_name: %s" % scan_results[id]["task_name"])
    logger.info("task_type: %s" % scan_results[id]["task_type"])
    logger.info("task_date: %s" % scan_results[id]["task_date"])
    
    
    process = Process(target=exec_wana, args=(id, wasm_filepath, output_filepath, task_type))
    process.start()



def exec_wana(id, wasm_filepath, output_filepath, task_type='EOSIO'):
    try:

        command = []
        
        # check task type
        if task_type != "EOSIO" and task_type != "Ethereum":
            raise Exception("Invalid task type.")
        
        # EOSIO smart contract
        if task_type == "EOSIO":
            # python3 wana.py -e contract.wasm
            command = ['python3', 'WANA/wana.py', '-o', str(output_filepath), '-e', str(wasm_filepath)]
        # Ethereum smart contract
        elif task_type == "Ethereum":
            # python3 wana.py --sol -e ethereum_contract.wasm
            command = ['python3', 'WANA/wana.py', '--sol', '-o', str(output_filepath), '-e', str(wasm_filepath)]
        
        # record execute time
        
        start_time = datetime.now()
        
        try:
            logger.info("executing command: %s" % command)
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            result = "Error executing command: {}".format(e)
        
        end_time = datetime.now()
        
        duration_time = end_time - start_time
        
        with open('scan_results_list.pickle', 'rb') as file:
            scan_results = pickle.load(file)
        
        scan_results[int(id)]["task_status"] = "Finished"
        scan_results[int(id)]["task_duration_time"] = str(duration_time)
                
        scan_report = {
            "fake-eos": False,
            "forged-transfer-notification": False,
            "block-dependency": False,
            "delegate-call": False,
            "greedy": False,
            "mishandled-exception": False,
            "reentrancy": False,
            "no-vulnerability": False
        }
        
        with open(output_filepath+'.pickle', 'rb') as file:
            scan_report = pickle.load(file)
        
        for key, value in scan_report.items():
            if value == True:
                scan_results[int(id)]["task_result"] = key
                break
        
        
        with open('scan_results_list.pickle', 'wb') as file:
            pickle.dump(scan_results, file)
        
        print(scan_results)
        
       
        
    except Exception as e:
        logger.error("Error: %s" % e)
        return "Error: %s" % e

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
            task_type = request.form.get('contract_category')
            filename = file.filename
                 

            # 確認是否有上傳檔案              
            if file.filename != '':
                uploading = True  # 開始上傳
                
                now = datetime.now()
                str_time = now.strftime("%d/%m/%Y %H:%M:%S")
                file_str_time = now.strftime("%d%m%Y%H%M%S")
                
                # 儲存檔案到指定位置
                wasm_filepath = os.path.join(UPLOAD_FOLDER, username, file.filename)
                result_filepath = os.path.join(RESULT_FOLDER, username, task_name+'_'+file_str_time+'_result')
                file.save(wasm_filepath)
                
                logger.info("received file upload.")
                logger.info("save file at %s" % wasm_filepath)
                
                create_task(current_result_id + 1, "Scanning", task_name, task_type, filename, str(str_time), "Scanning", "Scanning", wasm_filepath, result_filepath)
                current_result_id += 1
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
    update_scan_results()
    
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

@main.route('/get_task_status/<id>', methods=['GET'])
@login_required
def get_task_status(id):
    update_scan_results()
        
        
    print(scan_results)
    try:
        data = {
            "task_status": scan_results[int(id)]["task_status"],
            "task_result": scan_results[int(id)]["task_result"],
            "task_duration_time": scan_results[int(id)]["task_duration_time"]
        }
    except:
        data = {
            "task_status": "scanning",
            "task_result": "scanning",
            "task_duration_time": "scanning"
        }
    
    return jsonify(data)