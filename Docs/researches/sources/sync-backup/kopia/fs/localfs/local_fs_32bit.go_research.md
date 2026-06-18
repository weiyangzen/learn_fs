## sources/sync-backup/kopia/fs/localfs/local_fs_32bit.go

Purpose: build-tagged non-Windows helper for platforms where syscall device IDs are represented as `int32`.

Important APIs/types/functions: `platformSpecificWidenDev(dev int32) uint64`.

Control flow, state, and persistence: pure conversion helper with no state. It casts platform device values into the cross-platform `uint64` fields used by `fs.DeviceInfo`.

Dependencies and integration points: used by `local_fs_nonwindows.go` to populate `Dev` and `Rdev`; build tags include darwin/openbsd and non-listed non-Windows architectures.

Risks and test signals: risk is build-tag drift or lossy conversion if platform syscall types change. Device filtering in `ignorefs` indirectly depends on this metadata being stable.
