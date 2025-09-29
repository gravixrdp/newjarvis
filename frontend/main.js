$(document).ready(function () {
  // Initialize Python-side (face auth flow)
  try {
    eel.init();
  } catch (e) {
    console.log("eel.init() not available yet:", e);
  }

  $(".text").textillate({
    loop: true,
    speed: 1500,
    sync: true,
    in: { effect: "bounceIn" },
    out: { effect: "bounceOut" },
  });

  $(".siri-message").textillate({
    loop: true,
    sync: true,
    in: { effect: "fadeInUp", sync: true },
    out: { effect: "fadeOutUp", sync: true },
  });

  // Browser SpeechRecognition (no Python mic)
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition || null;
  let recognition = null;
  let listening = false;
  let continuousMode = JSON.parse(localStorage.getItem("continuousMode") || "true");
  let pendingListen = false;

  function setStatus(listeningNow) {
    if (listeningNow) {
      $("#Oval").attr("hidden", true);
      $("#SiriWave").attr("hidden", false);
    } else {
      $("#SiriWave").attr("hidden", true);
      $("#Oval").attr("hidden", false);
    }
  }

  function playBeep(type) {
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const o = ctx.createOscillator();
      const g = ctx.createGain();
      o.connect(g);
      g.connect(ctx.destination);
      o.type = "sine";
      o.frequency.setValueAtTime(type === "start" ? 1000 : 600, ctx.currentTime);
      g.gain.setValueAtTime(0.0001, ctx.currentTime);
      g.gain.exponentialRampToValueAtTime(0.1, ctx.currentTime + 0.01);
      g.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.15);
      o.start();
      o.stop(ctx.currentTime + 0.16);
      setTimeout(() => ctx.close(), 250);
    } catch (e) {}
  }

  function createRecognizer() {
    if (!SR) return null;
    const rec = new SR();
    rec.lang = "en-US";
    rec.interimResults = false;
    rec.maxAlternatives = 1;

    rec.onstart = function () {
      listening = true;
      setStatus(true);
    };
    rec.onerror = function (e) {
      console.log("SpeechRecognition error:", e.error);
      listening = false;
      setStatus(false);
      if (continuousMode && !window.assistantSpeaking) {
        setTimeout(() => startListening(), 700);
      } else {
        pendingListen = true;
      }
    };
    rec.onend = function () {
      listening = false;
      setStatus(false);
      if (continuousMode && !window.assistantSpeaking) {
        setTimeout(() => startListening(), 350);
      } else {
        pendingListen = true;
      }
    };
    rec.onresult = function (event) {
      const transcript = event.results[0][0].transcript;
      if (transcript && transcript.trim() !== "") {
        $("#chatbox").val("");
        eel.senderText(transcript);
        eel.takeAllCommands(transcript);
      }
    };
    return rec;
  }

  function startListening() {
    if (!SR) {
      console.log("SpeechRecognition not supported in this browser.");
      return;
    }
    if (listening) return;
    recognition && recognition.abort && recognition.abort();
    recognition = createRecognizer();
    if (!recognition) return;
    try {
      playBeep("start");
      recognition.start();
    } catch (e) {
      console.log("SpeechRecognition start error:", e);
    }
  }

  function stopListening() {
    try {
      recognition && recognition.stop && recognition.stop();
      playBeep("stop");
    } catch (e) {}
  }

  // Called by controller.js when TTS finishes
  window.onAssistantTTSComplete = function () {
    if (continuousMode) {
      setTimeout(() => {
        if (!listening) startListening();
        pendingListen = false;
      }, 200);
    }
  };

  // Mic button toggles listening
  $("#MicBtn").show().on("click", function () {
    if (listening) {
      stopListening();
    } else {
      startListening();
    }
  });

  // Settings: toggle hands-free continuous mode
  $("#SettingBtn").on("click", function () {
    continuousMode = !continuousMode;
    localStorage.setItem("continuousMode", JSON.stringify(continuousMode));
    const msg = continuousMode ? "Hands-free mode ON" : "Hands-free mode OFF";
    try { eel.DisplayMessage(msg); } catch (e) {}
  });

  function PlayAssistant(message) {
    if (message && message.trim() !== "") {
      eel.takeAllCommands(message);
      $("#chatbox").val("");
      $("#SendBtn").attr("hidden", true);
      if (continuousMode && !listening) startListening();
    } else {
      console.log("Empty message, nothing sent.");
    }
  }

  function ShowHideButton(message) {
    if (!message || message.length === 0) {
      $("#SendBtn").attr("hidden", true);
    } else {
      $("#SendBtn").attr("hidden", false);
    }
  }

  $("#chatbox").keyup(function () {
    let message = $("#chatbox").val();
    ShowHideButton(message);
  });

  $("#SendBtn").click(function () {
    let message = $("#chatbox").val();
    PlayAssistant(message);
  });

  $("#chatbox").keypress(function (e) {
    const key = e.which || e.keyCode;
    if (key === 13) {
      let message = $("#chatbox").val();
      PlayAssistant(message);
    }
  });
});
