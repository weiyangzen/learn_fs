## sources/sync-backup/syncthing/lib/fs/basicfs_fileinfo_windows.go

Purpose: Windows implementation of `basicFileInfo` mode normalization, executable-bit synthesis, ownership placeholders, and same-file conversion.

Important APIs/types/functions: `execExts` initialized from `PATHEXT`; `isWindowsExecutable`; `basicFileInfo.Mode`, `Owner`, `Group`, and `osFileInfo`.

Control flow: Init lowercases executable extensions from environment. Mode clears symlink bit for nonzero-size dedup/hardlink-like files, adds execute bits for executable extensions, and clears group/other write bits to avoid exporting world-writable permissions. Owner/group return -1. `osFileInfo` unwraps directory junction wrappers.

State and persistence: Reads environment at init; metadata view only.

Dependencies and integration points: Windows filesystem metadata, cross-platform permission synchronization, and directory junction support.

Risks: PATHEXT-dependent executable detection can vary by environment. Permission normalization is intentionally lossy.

Test signals: Windows basic filesystem tests outside this subset cover path and metadata behavior.
