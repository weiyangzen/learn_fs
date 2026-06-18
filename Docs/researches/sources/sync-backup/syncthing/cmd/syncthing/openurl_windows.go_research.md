# sources/sync-backup/syncthing/cmd/syncthing/openurl_windows.go

## Purpose
This Windows-only Go file implements `openURL(url string) error` using the native Windows shell association mechanism. It is the Windows counterpart to the Unix implementation and lets Syncthing open its GUI URL through the user's configured default browser.

## Important APIs, Types, And Functions
The file exposes only `openURL`. It converts the URL and the `"open"` verb to UTF-16 pointers via `windows.UTF16PtrFromString`, then calls `windows.ShellExecute` with `SW_SHOWNORMAL`. It imports `golang.org/x/sys/windows` rather than invoking `cmd.exe` or `rundll32`.

## Control Flow
`openURL` first converts `url` to a UTF-16 pointer and returns conversion errors immediately. It then converts the verb string and returns that error if it occurs. Finally it calls `ShellExecute` with no owner window, no parameters, no working directory, and normal show mode, returning the resulting error value directly.

## State And Persistence Behavior
The function does not modify Syncthing configuration or files. Its observable side effect is delegated to Windows ShellExecute, which may start a browser process, reuse an existing browser instance, or display a shell-level error depending on file association and desktop state.

## Dependencies And Integration Points
This function is selected by the `windows` build tag and shares the same package-level signature as the Unix implementation. Call sites in `cmd/syncthing/main.go` use it for GUI browser startup and explicit browser-opening commands. It relies on Windows URL association configuration and the `golang.org/x/sys/windows` syscall wrapper.

## Risks And Edge Cases
`UTF16PtrFromString` rejects strings containing NUL bytes, so malformed input is stopped before the syscall. `ShellExecute` behavior depends heavily on user profile, desktop session, and registry associations; service or headless contexts may fail or do nothing visible. Because the return is the syscall wrapper's error, callers need to handle platform-specific shell errors. The file has no URL scheme allow-list; it assumes callers pass the GUI URL or another trusted URL.

## Test Signals
There are no direct unit tests. The practical signals are Windows package builds and manual tests for `syncthing browser` or automatic GUI opening in an interactive Windows session.
