<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/mountinfo.go -->
# sources/user-network-fs/bazil-fuse/fs/fstestutil/mountinfo.go

Purpose: small cross-platform API for querying mount information relevant to tests.

Important APIs, types, and functions: defines `MountInfo` with `FSName` and `Type`, and exported `GetMountInfo` delegating to platform-specific `getMountInfo`.

Control flow: one wrapper call routes to the selected OS implementation.

State and persistence behavior: read-only query helper; no persistent state.

Dependencies and integration points: used by tests needing to assert FUSE mount type/name.

Risks and test signals: platform support differs; FreeBSD returns a fixed error while Linux parses `/proc/mounts`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/mountinfo.go -->
