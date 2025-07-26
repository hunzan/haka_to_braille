document.addEventListener('DOMContentLoaded', function () {
  // 轉換台羅拼音為台語點字
  function convertBraille() {
    const text = document.getElementById("inputText").value.trim();
    const inputMode = document.getElementById("inputType").value; // 取得輸入模式

    if (text === "") {
      alert("請輸入客語拼音，使用音調調號，不要用數字調號喔！");
      return;
    }

    fetch("/convert", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, inputMode })  // ✅ 把 inputMode 傳給後端
    })
      .then(response => response.json())
      .then(data => {
        const brailleOutput = document.getElementById("outputBraille");
        brailleOutput.value = data.braille;

                // 自動複製功能
        brailleOutput.focus();
        brailleOutput.select();

        try {
          const success = document.execCommand("copy");
          const status = success ? "點字內容已自動複製到剪貼簿" : "點字轉換完成，但自動複製失敗。";
          document.getElementById("copyStatus").textContent = status;
        } catch (err) {
          console.error("複製時發生錯誤：", err);
          document.getElementById("copyStatus").textContent = "點字轉換完成，但複製失敗。";
        }
      })
      .catch(error => {
        console.error("錯誤發生：", error);
        alert("轉換失敗，請稍後再試！");
    });
  }

  // 手動複製功能
  document.getElementById("copyBtn").addEventListener("click", function () {
    const brailleText = document.getElementById("outputBraille").value;
    if (!brailleText) {
      alert("目前沒有可複製的點字內容！");
      return;
    }

    navigator.clipboard.writeText(brailleText)
      .then(() => alert("點字內容已複製到剪貼簿！"))
      .catch(err => {
        console.error("複製失敗:", err);
        alert("無法複製點字，請手動選取！");
      });
  });

  // 清空輸入與輸出欄位
  function clearText() {
    document.getElementById("inputText").value = "";
    document.getElementById("outputBraille").value = "";
    document.getElementById("copyStatus").textContent = "";
  }

  // 欄位背景顏色調整
  document.getElementById("bgColor").addEventListener("input", (e) => {
    const color = e.target.value;
    document.getElementById("inputText").style.backgroundColor = color;
    document.getElementById("outputBraille").style.backgroundColor = color;
  });

  // 欄位文字顏色調整
  document.getElementById("textColor").addEventListener("input", (e) => {
    const color = e.target.value;
    document.getElementById("inputText").style.color = color;
    document.getElementById("outputBraille").style.color = color;
  });

  // 字體大小調整
  const fontSizeSlider = document.getElementById("fontSizeSlider");
  fontSizeSlider.addEventListener("input", () => {
    const size = fontSizeSlider.value + "px";
    document.getElementById("inputText").style.fontSize = size;
    document.getElementById("outputBraille").style.fontSize = size;
   document.getElementById("fontSizeValue").textContent = size;

  });

  // 按鈕綁定
  document.getElementById("convertBtn").addEventListener("click", convertBraille);
  document.getElementById("clearBtn").addEventListener("click", clearText);
});