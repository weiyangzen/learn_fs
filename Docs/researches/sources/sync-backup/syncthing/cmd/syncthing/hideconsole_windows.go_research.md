# sources/sync-backup/syncthing/cmd/syncthing/hideconsole_windows.go

Purpose: Windows build-specific CLI option definition for hiding the console.

Important APIs/types: `buildSpecificOptions` with `HideConsole` exposed as `--no-console` and environment `STHIDECONSOLE`.

Control flow and state: when selected by Windows builds, `serveCmd.Run` can call `osutil.HideConsole()` if this flag is set.

Dependencies/integration: embedded in `serveCmd` in `main.go` and tied to Windows console behavior.

Risks and test signals: option text notes Windows 11 24H2 behavior. No direct tests.
