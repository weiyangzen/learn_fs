# sources/sync-backup/syncthing/lib/versioner/external.go

Purpose: external command-based file versioner.

Important APIs and control flow: `init` registers factory `external`. `newExternal` reads the configured command and escapes backslashes on Windows. `Archive` lstat-checks the file, ignores nonexistent files, panics on symlinks, validates command presence, shell-splits the command, substitutes `%FOLDER_FILESYSTEM%`, `%FOLDER_PATH%`, and `%FILE_PATH%`, executes it with environment variables filtered to remove `STGUIAUTH` and `STGUIAPIKEY`, logs combined output, and succeeds only if the file no longer exists. `GetVersions` and `Restore` return `ErrRestorationNotSupported`; `Clean` is a no-op.

State and persistence: external command can perform arbitrary filesystem side effects; this code only verifies removal.

Dependencies and integration: uses folder filesystem abstraction, build OS flag, `go-shellquote`, and OS process execution.

Risks: command execution is powerful and configuration-controlled. Placeholder substitution occurs after shell splitting, so paths with spaces are passed as one arg only when placeholder occupies a quoted/split word appropriately. Tests cover missing command and successful quoted removal.
