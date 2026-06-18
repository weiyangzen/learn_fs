# sources/sync-backup/syncthing/gui/default/syncthing/core/uniqueFolderDirective.js

## Purpose
This AngularJS validation directive prevents adding a new folder with an ID that already exists in the current GUI folder map.

## Important APIs, Control Flow, And State
The directive registers `uniqueFolder`, requires `ngModel`, and prepends a parser to the model pipeline. For non-new folder editing modes, it marks the `uniqueFolder` validity key as true and does not enforce uniqueness. For new folders, it checks `scope.folders.hasOwnProperty(viewValue)` and sets validity false when the folder ID already exists. It returns the original `viewValue` unchanged.

## Dependencies And Integration Points
It depends on `scope.currentFolder._editing` and `scope.folders`, both maintained by `syncthingController.js`. It integrates with Angular form validity and folder editor templates.

## Risks And Test Signals
The directive assumes `scope.currentFolder` and `scope.folders` exist. If the parser runs before controller initialization, templates should prevent undefined access or tests will catch it. It validates only against the currently loaded local folder map; backend-side uniqueness remains the final guard. Unit tests should exercise new, existing, and defaults editing modes.
