# sources/test-tools/strace/src/statx.h

Purpose: local definition of `statx` timestamp and result structures for stable decoding across build hosts.

Important APIs/types/functions: `struct_statx_timestamp` and `struct_statx` with mask, block size, attributes, ownership, mode, inode, size, blocks, timestamps, device ids, mount id, DIO alignment, subvolume, atomic write fields, DIO read alignment, optimized atomic write size, and reserved space.

Control flow: header only; `statx.c` fetches and interprets this layout.

State and persistence behavior: none.

Dependencies and integration points: included by `statx.c`; supplements kernel/libc headers so strace can decode newer fields even on older build environments.

Risks: must exactly match Linux UAPI layout, including reserved padding. Adding fields in the wrong order breaks all downstream field decoding.

Test signals: compile-time layout checks where available, statx syscalls returning newer fields, and builds on older libc/kernel-header environments.
