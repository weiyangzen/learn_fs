# sources/sync-backup/syncthing/lib/versioner/staggered.go

Purpose: staggered retention file versioner that keeps dense recent versions and sparse older versions.

Important APIs and control flow: `init` registers factory `staggered`. `newStaggered` reads `maxAge` defaulting to about one year and configures four intervals: 30 seconds for first hour, one hour for next day, one day for next 30 days, and one week until max age. `Clean` delegates global cleanup. `toRemove` sorts versions, parses timestamp tags, removes versions older than max age, keeps the oldest first version as an anchor, then removes versions whose age spacing from the previous kept version is below the interval step. `Archive`, `GetVersions`, and `Restore` use shared helpers with `TagFilename`; `String` returns pointer identity.

State and persistence: archives source files to versions filesystem and deletes versions selected by retention logic.

Dependencies and integration: config params, fs abstraction, local time, and shared versioner helpers.

Risks: retention depends on filename timestamp parsing and local timezone. The algorithm iterates sorted filenames, so timestamp format order must remain lexicographic. Tests cover interval selection extensively.
