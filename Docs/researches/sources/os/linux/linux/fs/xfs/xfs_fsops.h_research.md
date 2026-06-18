# File Research: sources/os/linux/linux/fs/xfs/xfs_fsops.h

Declares filesystem-level operation entry points.

Key contents:
- Grow data/log APIs.
- Free-counter reserve-block tuning API.
- Filesystem going-down API.
- Per-AG metadata reservation init/free APIs.

This is the ioctl/mount-facing interface to growfs, reserve management, and administrative shutdown operations.
