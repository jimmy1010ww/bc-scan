function showConfirmation() {
    // 取得表單資訊
    var taskName = document.getElementsByName("task_name")[0].value;
    var contractCategory = document.getElementsByName("contract_category")[0].value;
    var file = document.getElementsByName("file")[0].value;

    // 印出確認訊息
    var confirmationMessage = "確認任務資訊：\n";
    confirmationMessage += "任務名稱: " + taskName + "\n";
    confirmationMessage += "合約種類: " + contractCategory + "\n";
    confirmationMessage += "上傳文件名稱: " + file + "\n";

    // 確認是否上傳
    var isConfirmed = confirm(confirmationMessage);

    // 如果確認上傳，則送出表單
    if (isConfirmed) {
        document.getElementsByClassName("upload-form")[0].submit();
    } else {
        return false; 
    }
}