# sources/user-network-fs/libfuse/lib/mount_util.c

## Purpose
Architecture-independent FUSE mount utility code: mount flag tables, mtab/utab update helpers, path resolution, FUSE device selection, and source/type string construction.

## Important APIs, Types, And Functions
- `mount_flags[]` maps option names to `MS_*`, safety, fsconfig, and mount-attribute metadata.
- `fuse_mnt_add_mount`, `fuse_mnt_remove_mount`, and `fuse_mnt_umount` update or bypass mtab/utab depending on platform and `/etc/mtab` state.
- `fuse_mnt_resolve_path` canonicalizes the parent path while preserving a final non-dot component.
- `fuse_mnt_get_devname` reads and validates `FUSE_KERN_DEVICE`.
- `fuse_mnt_build_source` and `fuse_mnt_build_type` centralize legacy and modern FUSE source/type formatting.
- `fuse_mnt_parse_fuse_fd` recognizes `/dev/fd/<n>` mountpoints.

## Control Flow
For mtab updates, the code decides whether `/etc/mtab` needs updates; if so it forks, blocks `SIGCHLD`, temporarily sets real uid to effective uid, and execs `/bin/mount` or `/bin/umount` with fake/no-canonicalize flags. Path resolution trims trailing slashes, resolves the parent, then appends the last component if it should not be resolved. Device resolution accepts only `/dev/...` character devices when present.

## State And Persistence
Persistent effects are mtab/utab entries and unmount records. Runtime state is only local allocation and process uid/signal mask manipulation. `FUSE_KERN_DEVICE` can redirect the device path within `/dev`.

## Dependencies And Integration Points
Used by libfuse mount code, `fusermount3`, `mount.fuse3`, service-mount helpers, and configuration checks. Platform branches support BSD and systems where mtab should be ignored.

## Risks
The fork/exec helpers depend on `/bin/mount` and `/bin/umount` behavior and carefully controlled environment. The source snapshot contains suspicious duplicate declarations/lines in `fuse_mnt_parse_fuse_fd` and `add_mount` output (`unsigned int fd;` duplicated and a repeated exec argument line), which should be checked against upstream or compilation logs. Device override validation rejects non-`/dev` paths but allows nonexistent `/dev/...` paths to fail later.

## Test Signals
Test mtab present, missing, symlinked, read-only, and `/run/mount/utab` cases; device override validation; source/type construction for `fuse`, `fuseblk`, subtype, and legacy subtype prefix; `/dev/fd` parsing including overflow; BSD `IGNORE_MTAB` builds.
