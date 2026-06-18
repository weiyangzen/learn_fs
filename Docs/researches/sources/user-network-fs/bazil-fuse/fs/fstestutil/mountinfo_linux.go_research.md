<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/mountinfo_linux.go -->
# sources/user-network-fs/bazil-fuse/fs/fstestutil/mountinfo_linux.go

Purpose: Linux implementation of `GetMountInfo` by parsing `/proc/mounts`.

Important APIs, types, and functions: defines `fstabUnescape`, `errNotFound`, and `getMountInfo`.

Control flow: sleeps briefly to reduce a known race, reads `/proc/mounts`, splits lines into fields, unescapes fsname/dir/type, and returns the entry matching the mount directory.

State and persistence behavior: read-only snapshot of procfs mount state.

Dependencies and integration points: depends on Linux `/proc/mounts` fstab-style escaping and is used by test assertions.

Risks and test signals: the fixed sleep hints at mount visibility races. Tests should cover escaped paths and not-found behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/mountinfo_linux.go -->
