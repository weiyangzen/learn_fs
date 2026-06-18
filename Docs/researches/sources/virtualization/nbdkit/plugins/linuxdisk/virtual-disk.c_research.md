# File Research: sources/virtualization/nbdkit/plugins/linuxdisk/virtual-disk.c

This file owns the linuxdisk virtual disk object lifecycle and region layout.

Key behavior:
- `init_virtual_disk` zeroes state, sets fd to `-1`, and initializes regions.
- `create_virtual_disk` allocates GPT/MBR buffers, creates the filesystem temp file, generates a random 16-byte partition GUID, builds regions, then fills partition-table structures.
- `free_virtual_disk` frees regions and metadata buffers and closes the filesystem fd.
- `create_regions` lays out the disk as protective MBR, primary GPT header/table, aligned filesystem partition at sector 2048, secondary GPT table, and secondary GPT header.

Integration:
- Calls `create_filesystem` from `filesystem.c`.
- Calls `create_partition_table` from `partition-gpt.c`.
- Uses common `regions` helper to model sparse disk data.

Risks:
- Metadata allocation and filesystem creation happen before final partition metadata is filled, so ordering matters.
- GPT structures depend on the final `regions` virtual size.
