# Research: sources/user-network-fs/rclone/fs/rc/disks.go

## sources/user-network-fs/rclone/fs/rc/disks.go

Purpose: platform-supported implementation of `getMounts` for `core/disks`, compiled except on `netbsd/386`. It uses `gopsutil/v4/disk.Partitions(false)` and returns each partition mountpoint.

Control flow ignores the partitions error, iterates all returned partitions, and appends `Mountpoint` strings. State and persistence are none. Dependencies are `github.com/shirou/gopsutil/v4/disk` and build tags. Integration point is `rcDisks` in `internal.go`, which filters these mount points through `mountOK` and combines them with home/root/user dirs. Risks include silently returning no mounts on gopsutil error, platform-specific mount naming, and potentially including duplicate or inaccessible mountpoints before later filtering. Test coverage for final disk output is in `internal_test.go`, not this file directly.
