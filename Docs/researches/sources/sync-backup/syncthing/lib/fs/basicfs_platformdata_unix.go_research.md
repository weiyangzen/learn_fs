## sources/sync-backup/syncthing/lib/fs/basicfs_platformdata_unix.go

Purpose: Non-Windows bridge from `BasicFilesystem` to Unix platform metadata collection.

Important APIs/types/functions: `BasicFilesystem.PlatformData`.

Control flow: Delegates to `unixPlatformData` with filesystem root/name, user/group caches, ownership and xattr scan flags, and xattr filter.

State and persistence: Reads metadata/xattrs depending on flags; uses caches owned by `BasicFilesystem`.

Dependencies and integration points: Integrates basic filesystem with protocol `PlatformData` for Unix ownership and xattrs.

Risks: Behavior depends on `unixPlatformData` and xattr support outside this file.

Test signals: Platform data/xattr tests are outside this subset.
