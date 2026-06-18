# File Research: sources/os/bsd/netbsd-src/sys/fs/tmpfs/tmpfs_args.h

Read completely: 54 lines.

This public mount-argument header defines `TMPFS_ARGS_VERSION` and `struct tmpfs_args`. Arguments include maximum inode count, maximum size, and root node uid/gid/mode.

Important interactions: `tmpfs_mount` validates the version and data length, derives default memory and node limits when values are small, supports `MNT_GETARGS`, and permits update mounts to adjust limits and root attributes.

Security/reliability notes: mount-time validation rejects bad version, bad uid/gid sentinels, and limit shrink attempts that conflict with current usage.
