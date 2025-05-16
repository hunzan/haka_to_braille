document.addEventListener('DOMContentLoaded', function () {
  // 轉換台羅拼音為台語點字
  function convertBraille() {
    const text = document.getElementById("inputText").value.trim();
    if (text === "") {
      alert("請輸入台羅拼音！");
      return;
    }

    fetch("/convert", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    })
      .then(response => response.json())
      .then(data => {
        const brailleOutput = document.getElementById("outputBraille");
        brailleOutput.value = data.braille;

        // 自動複製功能（使用 document.execCommand 確保支援度）
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
      .then(() => {
        alert("點字內容已複製到剪貼簿！");
      })
      .catch((err) => {
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

  // 更新背景顏色與字體顏色
  document.getElementById("bgColor").addEventListener("input", (e) => {
    document.body.style.backgroundColor = e.target.value;
  });

  document.getElementById("fontColor").addEventListener("input", (e) => {
    document.body.style.color = e.target.value;
  });

  // 更新字體大小
  const slider = document.getElementById('fontSizeSlider');
  const fontSizeValue = document.getElementById('fontSizeValue');
  const brailleDisplay = document.getElementById('outputBraille');

  if (slider && fontSizeValue && brailleDisplay) {
    slider.addEventListener('input', function () {
      const size = `${this.value}px`;
      fontSizeValue.textContent = size;
      brailleDisplay.style.fontSize = size;
    });
  }

  // 綁定按鈕事件
  document.getElementById("convertBtn").addEventListener("click", convertBraille);
  document.getElementById("clearBtn").addEventListener("click", clearText);
});
