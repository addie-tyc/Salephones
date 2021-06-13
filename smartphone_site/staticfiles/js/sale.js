document.querySelector("#images").addEventListener("change", function() {
    if (document.querySelector("#images").files.length > 4) {
        alert("最多只能上傳 4 張圖片");
        document.querySelector("#images").value = ""
        }
    }
)