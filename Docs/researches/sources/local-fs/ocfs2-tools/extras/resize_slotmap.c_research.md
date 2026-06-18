# File Research: sources/local-fs/ocfs2-tools/extras/resize_slotmap.c

Read coverage: complete file read, 185 lines.

Purpose: write-capable utility to change the logical size of the OCFS2 `//slotmap` system file.

Behavior:
- Usage: `resize_slotmap <device> <size>`.
- Warns that running against a mounted filesystem can damage it and asks for confirmation.
- Opens the volume read-write.
- Looks up and reads the slot-map system inode.
- Validates it is a valid system inode.
- Rejects requested sizes larger than allocated clusters or smaller than `OCFS2_MAX_SLOTS * sizeof(struct ocfs2_extended_slot)`.
- Asks for a second confirmation, then updates `i_size` and `i_mtime`.

Dependencies: cached inode APIs, slot-map system inode lookup, OCFS2 byte/cluster conversion.

Risk notes:
- Direct metadata mutation; intended for offline use.
- The file contains an unused `INSTALL_SIGNAL` macro referencing `handle_signal`, but no signal handler is defined or installed.
- Exits `0` even when resize/open errors are reported.
