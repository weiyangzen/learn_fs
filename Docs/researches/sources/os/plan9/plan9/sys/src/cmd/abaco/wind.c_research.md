# File Research: sources/os/plan9/plan9/sys/src/cmd/abaco/wind.c

Window object management for Abaco.

Key responsibilities:
- Initializes windows with tag, URL field, page, status field, and history.
- Resizes window subregions and page area.
- Closes windows and associated page/history/text state.
- Provides window locking.
- Builds tag text from page/window state.
- Updates URL and status text fields.
- Adds and navigates history entries.
- Hit-tests points to tag, URL, status, or page.
- Dispatches typing and mouse events to the correct subcomponent.
- Reports cleanliness and emits debug info.

Dependencies:
- Uses `Text`, `Page`, `Url`, column layout, Plan 9 draw/frame APIs, and history helpers.

Notable risks:
- History owns `Url` references and must release them correctly.
- Window layout assumes minimum heights for tag, URL, status, and page regions.
