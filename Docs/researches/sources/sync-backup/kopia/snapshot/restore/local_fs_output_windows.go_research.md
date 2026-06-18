# sources/sync-backup/kopia/snapshot/restore/local_fs_output_windows.go

Purpose: Windows-specific symlink attribute handling for local filesystem restore.

Important APIs/types/functions: `symlinkChown`, `symlinkChmod`, and `symlinkChtimes`. Ownership and mode changes are no-ops; timestamp updates use Windows file APIs.

Control flow: `symlinkChtimes` converts access and write times to `windows.Filetime`, normalizes long filenames with `ospath.SafeLongFilename`, opens the reparse point with `FILE_FLAG_OPEN_REPARSE_POINT`, and calls `windows.SetFileTime`.

State and persistence: only symlink timestamps are modified. Chown/chmod are skipped because Windows restore metadata does not map cleanly to POSIX UID/GID/mode.

Dependencies and integration points: selected on Windows and used by `FilesystemOutput.setAttributes`.

Risks and test signals: handle opening requires suitable permissions and sharing flags; failures propagate through restore unless permission errors are ignored. Long path conversion is essential for deep restore targets.
