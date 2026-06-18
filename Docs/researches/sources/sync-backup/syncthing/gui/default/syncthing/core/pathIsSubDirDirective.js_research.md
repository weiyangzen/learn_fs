# sources/sync-backup/syncthing/gui/default/syncthing/core/pathIsSubDirDirective.js

## Purpose
This directive adds Angular model validation-side effects for folder path forms, detecting whether the current folder path is a subdirectory of another configured folder or a parent of another configured folder.

## Important APIs, types, and functions
It registers attribute directive `pathIsSubDir` requiring `ngModel`. The directive adds `ctrl.$validators.folderPathErrors = function(viewValue) { ... }`. Inside, helper `isSubDir(xdir, ydir)` normalizes leading `~` using `scope.system.tilde` and `scope.system.pathSeparator`, splits paths, trims a trailing empty segment from `xdir`, and checks whether all `xdir` path components match the corresponding prefix of `ydir`.

## Control flow
For each validation run, it resets `scope.folderPathErrors` flags and metadata, returns true immediately for empty input, then iterates every folder in `scope.folders` except `scope.currentFolder.id`. If an existing folder path is a prefix of the new value, it marks `isSub`; if the new value is a prefix of an existing folder path, it marks `isParent`. It records the other folder's ID and label and breaks after the first match. The validator always returns true, so it does not invalidate the field; it only populates warning/error state for the template.

## State and persistence behavior
The directive mutates `scope.folderPathErrors` on the parent/current scope. It does not persist data or block saving directly through Angular validity.

## Dependencies and integration points
It depends on `ngModel`, `scope.system.pathSeparator`, `scope.system.tilde`, `scope.folders`, `scope.currentFolder`, and `scope.folderPathErrors`. It integrates with edit-folder templates that display subdirectory/parent-directory warnings and with controller-provided folder maps.

## Risks
Because the validator always returns true, any prevention must happen elsewhere; otherwise this is advisory only. Path comparison is string/component based and does not resolve symlinks, relative paths, case-insensitive filesystems, `.`/`..`, or Windows drive normalization beyond separator splitting. The tilde expansion regex uses template literals and assumes modern JavaScript support. It trims only `xdir` trailing separators, not `ydir`, which may affect equality and trailing-separator cases.

## Test signals
Tests should cover subdirectory, parent-directory, equal paths, trailing separators, tilde expansion, current-folder exclusion, Windows and Unix separators, empty input, and advisory return value behavior. UI tests should verify the correct other folder ID/label appears.
