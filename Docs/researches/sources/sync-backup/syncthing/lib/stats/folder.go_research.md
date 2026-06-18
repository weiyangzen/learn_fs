# sources/sync-backup/syncthing/lib/stats/folder.go

Purpose: stores and retrieves per-folder last-file and scan-completion statistics in typed KV storage.

Important APIs and control flow: `FolderStatistics` exposes `LastFile` and `LastScan`. `LastFile` records timestamp, filename, and whether the received file was deleted. `GetLastFile` reads `lastFileAt`, `lastFileName`, and `lastFileDeleted`; missing timestamp or filename returns an empty `LastFile`. `ReceivedFile` writes those three keys sequentially with current time truncated to seconds. `ScanCompleted` writes `lastScan`. `GetLastScanTime` defaults to zero time when missing. `GetStatistics` combines both getters.

State and persistence: persists `lastFileAt`, `lastFileName`, `lastFileDeleted`, and `lastScan` in `db.Typed`.

Dependencies and integration: used by folder statistics APIs and model reporting.

Risks: `ReceivedFile` is not transactional; write failures can leave mixed old/new metadata. Missing boolean is treated as false. Tests in this batch do not directly cover folder stats.
