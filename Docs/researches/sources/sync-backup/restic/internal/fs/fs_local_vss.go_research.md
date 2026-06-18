# sources/sync-backup/restic/internal/fs/fs_local_vss.go

Purpose: Wraps the local filesystem with transparent Windows Volume Shadow Copy Service snapshot access.

Important APIs: `VSSConfig`, `ParseVSSConfig`, `ErrorHandler`, `MessageHandler`, `volumeFilter`, `LocalVss`, `NewLocalVss`, `DeleteSnapshots`, `OpenFile`, `Lstat`, `isMountPointIncluded`, and `snapshotPath`.

Control flow and state: `LocalVss` keeps maps of successful and failed snapshots keyed by lowercased volume, protected by an RW mutex. `snapshotPath` normalizes a path, skips UNC shares, lazily creates one VSS snapshot per volume, tracks excluded volumes/mount points, maps mount-point paths to their own snapshots when available, and falls back to the original path on unsupported or failed snapshot creation.

Dependencies and integration: Delegates real filesystem operations to `NewLocal`; calls VSS functions from `vss_windows.go` or stubs from `vss.go`; uses `options` registration on Windows.

Risks: Snapshot creation is side-effectful and privilege-dependent. Fallback to original paths preserves backup progress but weakens consistency. Mount-point mapping is case-insensitive and relies on correct volume normalization.

Test signals: `fs_local_vss_test.go` covers config parsing, excluded volumes, provider parsing, and admin-only snapshot behavior.
