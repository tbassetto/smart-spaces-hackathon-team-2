const jsxapi = require("jsxapi");
const mqtt = require("mqtt");
const got = require("got");

const BOARD_IP = "192.168.1.187";
const RKMINI_IP = "192.168.1.197";

const WARNING_SCREEN =
  "https://cloud.appspace.com/app/#/tv/channelfullscreen/5859";
const CONTINUE_TO_THE_LEFT =
  "https://cloud.appspace.com/app/#/tv/channelfullscreen/5850";
const CONTINUE_TO_THE_RIGHT =
  "https://cloud.appspace.com/app/#/tv/channelfullscreen/5858";
const ATTENDEES_MAP =
  "http://192.168.1.246:8080/meeting/2755772e-365d-4f6b-8a0e-649fa259abd1/map";
// const MEETING_API = "http://192.168.1.246:8080/api/meeting/2755772e-365d-4f6b-8a0e-649fa259abd1";

// let meetingCache = {};
// got(MEETING_API)
//   .then(({ body }) => {
//     console.log("Got meeting data");
//     meetingCache = body;
//   })
//   .catch(error => {
//     console.error("No meeting data", error.response.body);
//   });

const board = jsxapi.connect(`ssh://${BOARD_IP}`, {
  username: "integrator",
  password: "integrator"
});
const rkmini = jsxapi.connect(`ssh://${RKMINI_IP}`, {
  username: "integrator",
  password: "integrator"
});

const mqttClient = mqtt.connect("mqtt://192.168.1.244", {
  clientId: "NeverLostLightController"
});
mqttClient.on("error", () => console.log("mqtt error", error));
mqttClient.on("connect", () => {
  console.log("MQTT connected");
  mqttClient.subscribe("person/help");
  mqttClient.subscribe("person/status");
  mqttClient.subscribe("person/webexboard");
  mqttClient.subscribe("XXX/YYY");
});
mqttClient.on("message", (topic, message) => {
  console.log("message.toString()", message.toString());
  try {
    message = JSON.parse(message.toString()); // message is Buffer
  } catch (e) {
    console.error(e);
    message = "{}";
  }
  console.log(`message from ${topic}`, message);
  if (topic === "person/help") {
    displayMessage(
      `${message.first_name} ${message.last_name} is lost`,
      "He is asking you to fetch him"
    );
  }
  if (topic === "person/status") {
    if (message.is_lost) {
      displayMessage(
        `${message.first_name} ${message.last_name} may be lost`,
        "He'll call for help if needed"
      );
    }
  }
  if (topic === "person/webexboard") {
    if (!message.is_lost) {
      openURL(CONTINUE_TO_THE_RIGHT);
    } else {
      openURL(WARNING_SCREEN);
    }
  }
  if (topic === "XXX/YYY") {
    openURL(ATTENDEES_MAP);
  }
});

board.on("error", err => {
  console.error("board error:", err);
});
board.on("ready", () => {
  console.log("board ready");
});
rkmini.on("error", err => {
  console.error("rkmini error:", err);
});
rkmini.on("ready", () => {
  console.log("rkmini ready");
});

// xAPI
function closeBrowser() {
  return board
    .command("Message Send", {
      Text: "BrowserClear"
    })
    .catch(err => {
      console.error("closeBrowser error", err);
    });
}

function openURL(url) {
  console.warn("openURL", url);
  return board
    .command("Message Send", {
      Text: `BrowserOpen@${url}`
    })
    .catch(err => {
      console.error("openURL error", err);
    });
}

function displayMessage(title, text) {
  console.log("displayMessage()", title, text);
  return rkmini
    .command("UserInterface Message Alert Display", {
      Title: title,
      Text: text
    })
    .catch(err => {
      console.error("displayMessage error", err);
    });
}
