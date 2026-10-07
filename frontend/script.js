function showToast(msg, type = "") {
    const t = document.getElementById("toast");
    t.textContent = msg;
    t.className = "toast show" + (type ? " " + type : "");
    setTimeout(() => { t.className = "toast"; }, 3200);
}

async function convert() {
    const text = document.getElementById("text").value.trim();

    if (!text) {
        showToast("Please enter some text first.", "error");
        return;
    }

    const btn = document.getElementById("convertBtn");
    btn.classList.add("loading");

    const token = localStorage.getItem("token");

    try {
        const response = await fetch("http://localhost:8000/speech/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ text })
        });

        if (!response.ok) {
            const error = await response.text();
            console.error(error);
            showToast("Conversion failed. Please try again.", "error");
            return;
        }

        const blob = await response.blob();
        const audioUrl = URL.createObjectURL(blob);

        const player  = document.getElementById("audioPlayer");
        const section = document.getElementById("audioSection");
        const wave    = document.getElementById("waveform");

        player.src = audioUrl;
        section.classList.add("visible");
        player.play();

        // Waveform sync
        wave.classList.add("playing");
        player.onplay   = () => wave.classList.add("playing");
        player.onpause  = () => wave.classList.remove("playing");
        player.onended  = () => wave.classList.remove("playing");

        showToast("Audio ready!", "success");

    } catch (err) {
        console.error(err);
        showToast("Something went wrong.", "error");
    } finally {
        btn.classList.remove("loading");
    }
}