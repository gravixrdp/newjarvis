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

  function startListening() {
    if (!SR) {
      console.log("SpeechRecognition not supported in this browser.");
      return;
    }
    const rec = new SR();
    rec.lang = "en-US";
    rec.interimResults = false;
    rec.maxAlternatives = 1;

    rec.onstart = function () {
      $("#Oval").attr("hidden", true);
      $("#SiriWave").attr("hidden", false);
    };
    rec.onerror = function (e) {
      console.log("SpeechRecognition error:", e.error);
      $("#SiriWave").attr("hidden", true);
      $("#Oval").attr("hidden", false);
    };
    rec.onend = function () {
      $("#SiriWave").attr("hidden", true);
      $("#Oval").attr("hidden", false);
    };
    rec.onresult = function (event) {
      const transcript = event.results[0][0].transcript;
      if (transcript && transcript.trim() !== "") {
        $("#chatbox").val("");
        eel.senderText(transcript);
        eel.takeAllCommands(transcript);
      }
    };

    try {
      rec.start();
    } catch (e) {
      console.log("SpeechRecognition start error:", e);
    }
  }

  // Mic button uses browser recognition
  $("#MicBtn").show().on("click", function () {
    startListening();
  });

  function PlayAssistant(message) {
    if (message && message.trim() !== "") {
      eel.takeAllCommands(message);
      $("#chatbox").val("");
      $("#SendBtn").attr("hidden", true);
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
