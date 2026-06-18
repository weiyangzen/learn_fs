# sources/sync-backup/syncthing/gui/default/syncthing/core/validDeviceidDirective.js

## Purpose
This AngularJS validation directive validates Syncthing device IDs through the backend and also flags IDs that are already present in the current configuration.

## Important APIs, Control Flow, And State
The directive registers `validDeviceid`, requires `ngModel`, injects `$http`, and prepends a parser. On every parsed view value, it calls `GET /svc/deviceid?id=<viewValue>`. The success handler treats `!resp.error` as syntactic validity and treats uniqueness as true when the ID is invalid or absent from `scope.devices`. It sets Angular validity keys `validDeviceid` and `unique`, then returns the original view value.

## Dependencies And Integration Points
It depends on the backend `/svc/deviceid` endpoint returning an `id` and optional `error`, plus `scope.devices` from the main controller. It integrates with Angular form validation for the device editor.

## Risks And Test Signals
Validation is asynchronous but implemented inside a synchronous parser without cancellation or stale-response protection. Rapid typing can allow older HTTP responses to update validity after newer input. The raw query parameter is not encoded, so unusual input characters could produce malformed URLs; `encodeURIComponent` would be safer. Unit or e2e tests should cover valid IDs, invalid IDs, duplicate IDs, and fast input changes.
