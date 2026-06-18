# File Research: sources/os/linux/linux/fs/ubifs/scan.c

Read completely: 366 lines.

This file implements the generic UBIFS logical eraseblock scanner. It identifies valid UBIFS nodes, padding nodes/bytes, empty space, and corrupt regions within one LEB.

Main entry points: `ubifs_scan_a_node`, `ubifs_start_scan`, `ubifs_end_scan`, `ubifs_add_snod`, `ubifs_scanned_corruption`, `ubifs_scan`, and `ubifs_scan_destroy`.

Key behavior: `ubifs_scan` reads a full LEB into a caller-provided buffer, then walks from the requested offset in 8-byte-aligned increments. Valid nodes are added to a `struct ubifs_scan_leb` list as `struct ubifs_scan_node` records; padding nodes or padding bytes advance the scan; empty space terminates node scanning and is then verified as all `0xff`.

Node classification: `ubifs_scan_a_node` recognizes erased space by `0xffffffff` magic, validates UBIFS common headers through `ubifs_check_node`, handles `UBIFS_PAD_NODE` length and alignment checks, and returns scanner status codes that distinguish valid nodes, corrupt nodes, bad padding, padding bytes, empty space, and garbage.

Scanned-node records: `ubifs_add_snod` records sequence number, type, offset, length, backing node pointer, and key for inode/dentry/xentry/data nodes. Non-keyed nodes receive an invalid key marker.

Error handling: scan corruption returns `-EUCLEAN` after optionally dumping up to 8192 bytes from the corrupt offset. Other I/O or allocation errors return their negative errno and destroy partial scan state.

Important interactions: journal replay, garbage collection, in-the-gaps TNC commit, and debug checks use this scanner to reason about LEB contents. It depends on `io.c` validation and uses caller-owned scan buffers, so scan-node `node` pointers refer into `sleb->buf`.

Reliability notes: integrity read errors from UBI are tolerated at `ubifs_start_scan` time because individual UBIFS nodes are CRC checked. Empty-space alignment to `min_io_size` is enforced before the trailing `0xff` verification.
