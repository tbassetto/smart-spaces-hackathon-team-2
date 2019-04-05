const xapi = require("xapi");

function guiEvent(event) {
  if (event.PanelId === "close_browser") {
    xapi.command("Message Send", {
      Text: "BrowserClear"
    });
  }
}

xapi.event.on("UserInterface Extensions Panel Clicked", guiEvent);
