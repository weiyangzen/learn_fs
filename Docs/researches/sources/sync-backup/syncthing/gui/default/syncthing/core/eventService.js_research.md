# sources/sync-backup/syncthing/gui/default/syncthing/core/eventService.js

## Purpose
This AngularJS service maintains the GUI's long-polling connection to Syncthing's REST event stream and broadcasts server events into Angular scope listeners.

## Important APIs, types, and functions
It registers service `Events` on `syncthing.core` and injects `$http`, `$rootScope`, and `$timeout`. Public constants include UI events `ONLINE` and `OFFLINE`, plus many server event type names such as `CONFIG_SAVED`, `DEVICE_CONNECTED`, `DOWNLOAD_PROGRESS`, `FOLDER_SUMMARY`, `ITEM_FINISHED`, `STATE_CHANGED`, and others. The public method `start()` begins polling with `GET rest/events?limit=1`.

## Control flow
`start()` fetches one event to establish `lastID`. `successFn(data)` treats empty data as failure, broadcasts `UIOnline`, broadcasts each returned Syncthing event only after the initial response, updates `lastID` to the last event ID, and immediately starts the next long poll with `GET rest/events?since=<lastID>`. `errorFn(statusString, status)` reloads the page on HTTP 403, broadcasts `UIOffline` for other failures, and schedules a retry after one second using `$timeout(..., false)` to avoid forcing a digest on the timer itself.

## State and persistence behavior
The service keeps `lastID` in closure state for event-stream continuity. It does not persist data across reloads. Online/offline status is distributed as Angular broadcasts rather than stored in the service.

## Dependencies and integration points
It depends on global `urlbase`, Angular's legacy `$http.success/.error` API, `$rootScope` event broadcasting, and the REST `/events` endpoint. Controllers register listeners for the constants or raw server event type names to refresh configuration, folder summaries, device state, progress, and notifications.

## Risks
Using `$http.success/.error` ties the code to AngularJS 1.x legacy APIs. If the first event response contains meaningful events, they are intentionally suppressed by the `lastID > 0` guard. `data.pop()` mutates the response array after broadcasting. A persistent failure creates an infinite retry loop every second. Empty HTTP 200 bodies are correctly treated as failures for restart scenarios, but callers must tolerate offline/online flapping during Syncthing restarts.

## Test signals
Tests should mock `$http` and `$timeout` to verify initial suppression, subsequent event broadcasts, `lastID` advancement, empty-success fallback to offline retry, 403 reload behavior, and retry URL selection. Integration tests should confirm controllers receive expected broadcasts from real `/rest/events` traffic.
