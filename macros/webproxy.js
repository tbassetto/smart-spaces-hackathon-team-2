const xapi = require("xapi");

// function message(text) {
//   xapi.command("UserInterface Message Alert Display", {
//     Text: text
//   });
// }

xapi.event.on("Message Send", event => {
  if (event.Text === "BrowserClear") {
    // message("xCommand UserInterface WebView Clear");
    xapi.command("UserInterface WebView Clear");
    return;
  }
  const parts = event.Text.split("@");
  if (parts[0] === "BrowserOpen") {
    // message(`xCommand UserInterface WebView Display Url: ${parts[1]}`);
    xapi.command("UserInterface WebView Display", {
      Url: parts[1]
    });
  }
});
