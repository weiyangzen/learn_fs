## sources/sync-backup/syncthing/lib/fs/basicfs_platformdata_windows.go

Purpose: Windows platform metadata collection for file owner names.

Important APIs/types/functions: `BasicFilesystem.PlatformData` and `openReadOnlyWithBackupSemantics`.

Control flow: If ownership scanning is disabled, returns empty platform data. Otherwise roots the path, opens it read-only with backup semantics so directories can be opened, calls `windows.GetSecurityInfo` for owner SID, resolves SID through user then group caches, and returns `protocol.PlatformData{Windows: ...}` with owner name and group flag when known.

State and persistence: Reads Windows security descriptors and uses filesystem user/group caches. No mutation.

Dependencies and integration points: Windows API, protocol WindowsData, BasicFilesystem rooting, value caches.

Risks: Owner lookup failures only debug-log and return empty owner fields. Opening with backup semantics and security APIs can fail due to permissions or filesystem behavior.

Test signals: Windows platform metadata tests are outside this subset.
