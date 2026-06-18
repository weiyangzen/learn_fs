# sources/sync-backup/syncthing/cmd/syncthing/hideconsole_others.go

Purpose: non-Windows build-specific CLI option definition.

Important APIs/types: `buildSpecificOptions` with hidden `HideConsole`.

Control flow and state: build tags select this file on non-Windows, keeping the `serveCmd` field portable while hiding the no-console option.

Dependencies/integration: embedded in `serveCmd` in `main.go`.

Risks and test signals: no runtime behavior on non-Windows. Build tag correctness is the main signal; no tests.
