# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/quota2_subr.c

This file provides quota2 format construction, byte swapping, and limit checking.

Key behavior:
- `quota2_addfreeq2e` adds all quota entries in a block to the free list.
- `quota2_create_blk0` initializes the quota2 header block, hash table, unlimited default limits, and seven-day grace defaults.
- `quota2_ufs_rwq2v` and `quota2_ufs_rwq2e` byte-swap quota values and entries.
- `quota_check_limit` returns allow/deny status for soft/hard limit enforcement and indicates soft-limit crossings.

Role:
- Shared helper code for kernel and tooling that understands quota2 layout.
