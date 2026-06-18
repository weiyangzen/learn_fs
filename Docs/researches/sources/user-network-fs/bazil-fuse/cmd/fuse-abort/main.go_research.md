<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/cmd/fuse-abort/main.go -->
# sources/user-network-fs/bazil-fuse/cmd/fuse-abort/main.go

Purpose: Linux command-line utility to forcibly abort and unmount hung FUSE mountpoints by writing to `/sys/fs/fuse/connections/<id>/abort`.

Important APIs, types, and functions: `findFUSEMounts`, `abort`, `pruneEmptyDir`, `run`, `usage`, and `main`. It uses `mountinfo.Open`, `fuse.Unmount`, `filepath.Abs`, and `syscall.Rmdir`.

Control flow: command-line parsing requires mountpoints and optional `-p`. `run` builds a mountpoint-to-connection map, processes arguments in order, validates each is a FUSE mount, writes `1` to sysfs abort, unmounts, and optionally prunes empty directories.

State and persistence behavior: modifies kernel FUSE connection state and mount state. Optional pruning removes only empty directories.

Dependencies and integration points: Linux-only build; depends on proc mountinfo, sysfs FUSE connection layout, and bazil fuse unmount logic.

Risks and test signals: races with unmount are treated as success for missing abort files. Risks include wrong mountpoint path resolution and privilege errors. Tests should mock mountinfo/sysfs or run in controlled namespaces.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/cmd/fuse-abort/main.go -->
