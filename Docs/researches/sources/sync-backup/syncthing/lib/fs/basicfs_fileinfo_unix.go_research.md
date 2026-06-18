## sources/sync-backup/syncthing/lib/fs/basicfs_fileinfo_unix.go

Purpose: Unix implementation of `basicFileInfo` mode, owner, group, and same-file conversion.

Important APIs/types/functions: `basicFileInfo.Mode`, `Owner`, `Group`, and `osFileInfo`.

Control flow: Mode directly converts underlying `os.FileMode`; owner/group inspect `*syscall.Stat_t` from `FileInfo.Sys()` and return UID/GID or -1; `osFileInfo` returns underlying info.

State and persistence: Read-only file metadata view.

Dependencies and integration points: Non-Windows build tag; used by `BasicFilesystem.Stat/Lstat`, ownership scan, and `SameFile`.

Risks: `Sys()` type assertion can fail for nonstandard `os.FileInfo`, yielding -1 ownership.

Test signals: Filesystem metadata tests outside this subset cover Unix behavior.
