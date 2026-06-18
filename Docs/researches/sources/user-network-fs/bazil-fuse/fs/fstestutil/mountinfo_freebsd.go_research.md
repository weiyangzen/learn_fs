<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/mountinfo_freebsd.go -->
# sources/user-network-fs/bazil-fuse/fs/fstestutil/mountinfo_freebsd.go

Purpose: FreeBSD implementation stub for test mount information.

Important APIs, types, and functions: `getMountInfo` returns an error stating FreeBSD has no useful mount information.

Control flow: all calls fail immediately.

State and persistence behavior: no state.

Dependencies and integration points: selected by Go build constraints on FreeBSD.

Risks and test signals: tests requiring mount info must skip or handle this error on FreeBSD.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/mountinfo_freebsd.go -->
