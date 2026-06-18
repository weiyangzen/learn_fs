## sources/sync-backup/kopia/fs/localfs/local_fs_nonwindows.go

Purpose: non-Windows metadata extraction for owner IDs, group IDs, and device identifiers.

Important APIs/types/functions: `isWindows`, `platformSpecificOwnerInfo`, `platformSpecificDeviceInfo`, and `trailingSeparator`.

Control flow, state, and persistence: reads `syscall.Stat_t` from `os.FileInfo.Sys()` and maps UID/GID and device fields into Kopia metadata. `trailingSeparator` is a no-op outside Windows.

Dependencies and integration points: feeds `filesystemEntry` metadata in `newEntry`; device data is consumed by filtering wrappers such as `ignorefs` one-filesystem mode.

Risks and test signals: risks include platform syscall variance and zero metadata when `Sys()` has an unexpected type. Permission-denied and traversal tests indirectly cover non-Windows behavior; device-specific correctness depends on platform integration tests.
