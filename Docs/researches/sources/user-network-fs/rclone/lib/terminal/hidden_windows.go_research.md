# sources/user-network-fs/rclone/lib/terminal/hidden_windows.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/terminal/hidden_windows.go -->
## sources/user-network-fs/rclone/lib/terminal/hidden_windows.go

Purpose: Windows implementation of console hiding.

Important APIs and control flow: `HideConsole()` lazily looks up `GetConsoleWindow` from `kernel32.dll` and `ShowWindow` from `user32.dll`. If both procedures are available and a console window handle exists, it calls `ShowWindow(hwnd, 0)` to hide it.

State, dependencies, and integration: no persistent state. It depends on `golang.org/x/sys/windows`. It integrates with GUI/daemon scenarios that should hide an inherited console window.

Risks and test signals: return values from `ShowWindow` are ignored; failure is silent. Behavior is Windows-only and untested in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/terminal/hidden_windows.go -->
