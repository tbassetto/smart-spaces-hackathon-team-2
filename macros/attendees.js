const xapi = require("xapi");

function widgetAction(event) {
  console.log("widgetAction", event);
  const parts = event.WidgetId.split("_");
  if (parts[0] === "attendee" && event.Type === "clicked") {
    console.log(
      `Sending BrowserOpen@http://192.168.1.246:8080/person/${parts[1]}/map`
    );
    if (parts[1] === "all") {
      xapi
        .command("Message Send", {
          Text: `BrowserOpen@http://192.168.1.246:8080/meeting/2755772e-365d-4f6b-8a0e-649fa259abd1/map`
        })
        .catch(error => console.error("oh no", error));
    } else {
      xapi
        .command("Message Send", {
          Text: `BrowserOpen@http://192.168.1.246:8080/person/${parts[1]}/map`
        })
        .catch(error => console.error("oh no", error));
    }
  }
}

function fetchAttendees() {
  console.log("fetchAttendees()");
  return xapi.command("HttpClient Get", {
    Url:
      "http://192.168.1.246:8080/api/meeting/2755772e-365d-4f6b-8a0e-649fa259abd1"
  });
}

function panelClicked(event) {
  console.log("panelClicked", event);
  if (event.PanelId === "panel_eta") {
    xapi.command("Message Send", {
      Text: "BrowserClear"
    });
    fetchAttendees()
      .then(data => {
        const response = JSON.parse(data.Body);
        console.log("response", response);
        const users = [response.host].concat(response.persons);
        const rowsXml = users.map(user => {
          return `<Row>
        <Name>Row</Name>
        <Widget>
          <WidgetId>attendee_${user.id}</WidgetId>
          <Name>${user.first_name} ${user.last_name} ${
            user.eta ? `(${Math.floor(user.eta + 1)} min)` : "(host)"
          }</Name>
          <Type>Button</Type>
          <Options>size=3</Options>
        </Widget>
      </Row>`;
        });

        return xapi.command(
          "UserInterface Extensions Panel Save",
          { PanelId: "panel_eta" },
          `<Extensions>
  <Version>1.5</Version>
  <Panel>
    <PanelId>panel_eta</PanelId>
    <Type>Statusbar</Type>
    <Icon>Input</Icon>
    <Order>2</Order>
    <Color>#00D6A2</Color>
    <Name>Attendees ETA</Name>
    <Page>
      <Name>Attendees</Name>
      <Row>
        <Name>Row</Name>
        <Widget>
          <WidgetId>attendee_all</WidgetId>
          <Name>All</Name>
          <Type>Button</Type>
          <Options>size=3</Options>
        </Widget>
      </Row>
      ${rowsXml}
      <PageId>attendees_panel</PageId>
      <Options>hideRowNames=1</Options>
    </Page>
  </Panel>
</Extensions>`
        );
      })
      .catch(error => console.error("Giving up", error));
  }
}

xapi.event.on("UserInterface Extensions Widget Action", widgetAction);
xapi.event.on("UserInterface Extensions Panel Clicked", panelClicked);
