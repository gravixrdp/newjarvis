$(document).ready(function () {
  // Browser TTS with best-voice selection and callback
  let cachedVoices = [];
  let preferredVoices = [
    "Google UK English Female",
    "Microsoft Zira",
    "Microsoft Sonia Online",
    "Microsoft Aria Online",
    "en-US",
    "en-GB",
  ];

  function refreshVoices() {
    try {
      cachedVoices = window.speechSynthesis ? speechSynthesis.getVoices() || [] : [];
    } catch (e) {
      cachedVoices = [];
    }
  }
  refreshVoices();
  if (window.speechSynthesis) {
    window.speechSynthesis.onvoiceschanged = refreshVoices;
  }

  function pickBestVoice() {
    if (!cachedVoices || cachedVoices.length === 0) return null;
    // Try exact matches first
    for (const name of preferredVoices) {
      const v = cachedVoices.find((vv) => (vv.name || "").toLowerCase().includes(name.toLowerCase()));
      if (v) return v;
    }
    // Fallback: first English voice
    const en = cachedVoices.find((v) => (v.lang || "").toLowerCase().startsWith("en"));
    if (en) return en;
    return cachedVoices[0];
  }

  function speakText(message) {
    try {
      if (!message || !window.speechSynthesis) return;
      const utter = new SpeechSynthesisUtterance(message);
      const v = pickBestVoice();
      if (v) utter.voice = v;
      utter.rate = 0.98;
      utter.pitch = 1.0;
      window.assistantSpeaking = true;
      utter.onend = function () {
        window.assistantSpeaking = false;
        if (typeof window.onAssistantTTSComplete === "function") {
          window.onAssistantTTSComplete();
        }
      };
      // Cancel any ongoing speech then speak
      speechSynthesis.cancel();
      speechSynthesis.speak(utter);
    } catch (e) {}
  }

  // Display Speak Message
  eel.expose(DisplayMessage);
  function DisplayMessage(message) {
    // Update the visible H1
    $("#WishMessage").text(message);
    // Also update any textillate targets if present
    $(".siri-message").text(message);
    try {
      $(".siri-message").textillate("start");
    } catch (e) {
      // textillate may not be initialized yet; ignore
    }
  }

  eel.expose(ShowHood);
  function ShowHood() {
    $("#Oval").attr("hidden", false);
    $("#SiriWave").attr("hidden", true);
  }

  eel.expose(senderText);
  function senderText(message) {
    var chatBox = document.getElementById("chat-canvas-body");
    if (message.trim() !== "") {
      chatBox.innerHTML += `<div class="row justify-content-end mb-4">
          <div class = "width-size">
          <div class="sender_message">${message}</div>
      </div>`;

      chatBox.scrollTop = chatBox.scrollHeight;
    }
  }

  eel.expose(receiverText);
  function receiverText(message) {
    var chatBox = document.getElementById("chat-canvas-body");
    if (message.trim() !== "") {
      chatBox.innerHTML += `<div class="row justify-content-start mb-4">
          <div class = "width-size">
          <div class="receiver_message">${message}</div>
          </div>
      </div>`;

      // Scroll to the bottom of the chat box
      chatBox.scrollTop = chatBox.scrollHeight;

      // Speak assistant responses via browser TTS
      speakText(message);
    }
  }
  eel.expose(hideLoader);
  function hideLoader() {
    $("#Loader").attr("hidden", true);
    $("#FaceAuth").attr("hidden", false);
  }
  // Hide Face auth and display Face Auth success animation
  eel.expose(hideFaceAuth);
  function hideFaceAuth() {
    $("#FaceAuth").attr("hidden", true);
    $("#FaceAuthSuccess").attr("hidden", false);
  }
  // Hide success and display
  eel.expose(hideFaceAuthSuccess);
  function hideFaceAuthSuccess() {
    $("#FaceAuthSuccess").attr("hidden", true);
    $("#HelloGreet").attr("hidden", false);
  }

  // Hide Start Page and display blob
  eel.expose(hideStart);
  function hideStart() {
    $("#Start").attr("hidden", true);

    setTimeout(function () {
      $("#Oval").addClass("animate__animated animate__zoomIn");
    }, 1000);
    setTimeout(function () {
      $("#Oval").attr("hidden", false);
    }, 1000);
  }
});
