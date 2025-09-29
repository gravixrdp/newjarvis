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

  // Hide microphone UI (text-only mode)
  $("#MicBtn").hide();

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
