## sources/sync-backup/syncthing/lib/osutil/hidden_windows.go

Purpose: Windows implementation for hiding the console window.

Important API: `HideConsole` dynamically looks up `GetConsoleWindow` and `ShowWindow`; if a console window exists it calls `ShowWindow(hwnd, 0)`.

Control flow and state: uses lazy DLL loading and only calls functions if lookup succeeds.

Dependencies and integration points: used by Windows GUI/background startup paths.

Risks: direct syscall use and window-handle handling are Windows-specific. Failures are silently ignored.

Test signals: no direct tests.
