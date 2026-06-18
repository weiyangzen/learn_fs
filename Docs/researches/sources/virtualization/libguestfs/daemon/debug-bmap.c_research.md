# File Research: sources/virtualization/libguestfs/daemon/debug-bmap.c

Interim debug APIs for virt-bmap-style cache/read mapping experiments.

Key points:
- Maintains static open file descriptor or directory handle prepared by `debug_bmap_file` or `debug_bmap_device`.
- Destructor closes any leftover fd/dir.
- `bmap_prepare` stats and opens either a directory or file/device, using sequential/no-reuse fadvise for regular reads.
- `debug_bmap` drops caches, reads the prepared file/device fully or iterates the prepared directory, then closes resources.
- Returns `"ok"` on successful prepare/read.
