# sources/sync-backup/kopia/internal/mount/mount_fuse.go

Purpose: implements POSIX non-FreeBSD/OpenBSD mounting through go-fuse, with optional fallback to WebDAV when requested.

Important APIs/types/functions: `Options.toFuseMountOptions`, `Directory`, `fuseController`, `Unmount`, `MountPath`, and `Done`; package `cacheTimeout` controls FUSE entry/attribute/negative cache durations.

Control flow: `Directory` creates a temporary directory for mount point `*`, routes to `newPosixWedavController` when `PreferWebDAV` is set, otherwise wraps the Kopia `fs.Directory` in a FUSE node and calls `gofusefs.Mount`. A goroutine waits on the FUSE server and closes `done`.

State and persistence behavior: controller stores mount path, FUSE server, done channel, and whether the mount point was temporary. Unmount calls FUSE unmount and removes temp directory.

Dependencies and integration points: uses `go-fuse`, `internal/fusemount`, `fs.Directory`, and environment variable `KOPIA_DEBUG_FUSE`.

Risks and test signals: temp directory cleanup only runs after successful unmount; mount option support is OS/FUSE-version sensitive. Integration tests need real FUSE availability, option propagation, `PreferWebDAV`, and temporary mount cleanup.
