## sources/sync-backup/kopia/fs/localfs/local_fs_64bit.go

Purpose: build-tagged non-Windows helper for platforms where syscall device IDs are already `uint64`.

Important APIs/types/functions: `platformSpecificWidenDev(dev uint64) uint64`.

Control flow, state, and persistence: identity function used when recording `fs.DeviceInfo`.

Dependencies and integration points: used by `local_fs_nonwindows.go` on common Linux-style architectures. It supports downstream one-filesystem comparisons.

Risks and test signals: risk is primarily incorrect build constraints for a new architecture. There are no direct unit tests, but one-filesystem and localfs traversal tests exercise resulting metadata on supported platforms.
