# Research: sources/user-network-fs/rclone/fs/rc/disks_unsupported.go

## sources/user-network-fs/rclone/fs/rc/disks_unsupported.go

Purpose: fallback `getMounts` implementation for `netbsd && 386`, where the gopsutil-backed disk implementation is excluded. It returns a single mount point, `"/"`.

Control flow and state are trivial: no dependencies beyond the local package and no persistence. Integration point is `rcDisks` in `internal.go`, which will include root and user directories and deduplicate paths. Risk is reduced functionality on this platform, since only root is surfaced as a mount candidate. The build tag makes correctness dependent on Go’s build selection. There is no direct unit test for this build-constrained file in the current platform run.
