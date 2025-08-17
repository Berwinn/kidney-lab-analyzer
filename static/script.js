const imageInput = document.getElementById("imageInput");
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");
const statusText = document.getElementById("statusText");
const labVal = document.getElementById("labVal");
const diagnosis = document.getElementById("diagnosis");
let uploadedImage = null;

imageInput.addEventListener("change", (e) => {
  const file = e.target.files[0];
  if (!file) return;

  const img = new Image();
  img.onload = () => {
    const maxWidth = 800;
    const scale = img.width > maxWidth ? maxWidth / img.width : 1;

    const newWidth = img.width * scale;
    const newHeight = img.height * scale;

    canvas.width = newWidth;
    canvas.height = newHeight;

    ctx.drawImage(img, 0, 0, newWidth, newHeight);
    uploadedImage = img;

    const centerX = Math.floor(canvas.width / 2);
    const centerY = Math.floor(canvas.height / 2);
    ctx.beginPath();
    ctx.arc(centerX, centerY, 100, 0, 2 * Math.PI);
    ctx.strokeStyle = "red";
    ctx.lineWidth = 3;
    ctx.stroke();

    if (statusText) statusText.textContent = "กำลังประมวลผล...";

    canvas.toBlob(async (blob) => {
      const formData = new FormData();
      formData.append("image", blob);
      formData.append("x", centerX);
      formData.append("y", centerY);

      try {
        const response = await fetch("/analyze", {
          method: "POST",
          body: formData,
        });

        const data = await response.json();
        const L = data.L;
        const a = data.a;
        const b = data.b;

        if (labVal) {
          labVal.textContent = `(${L.toFixed(2)}, ${a.toFixed(2)}, ${b.toFixed(2)})`;
        }

        // ✅ ตัดสินจากค่า a และ b เท่านั้น
        const isMicroAlbuminuria = a > -2 || b < 10;

        if (diagnosis) {
          if (isMicroAlbuminuria) {
            diagnosis.innerHTML = `
              <span class="danger">ภาวะไมโครอัลบูมินูเรีย</span><br/>
              วิธีรักษา: ควรรีบเข้ารับการตรวจสอบโดยแพทย์ผู้เชี่ยวชาญด่วน
            `;
          } else {
            diagnosis.innerHTML = `
              <span class="safe">ภาวะปกติ</span><br/>
              วิธีรักษา: รักษาสุขภาพและออกกำลังกายสม่ำเสมอ
            `;
          }
        }

      } catch (err) {
        alert("❌ เกิดข้อผิดพลาดในการวิเคราะห์");
        console.error(err);
      }

      if (statusText) statusText.textContent = "";
    });
  };

  img.src = URL.createObjectURL(file);
});
