# File Research: sources/os/bsd/netbsd-src/sys/sys/wapbl.h

Read completely: 278 lines.

Public/private header for NetBSD write-ahead physical block logging (WAPBL). It declares the kernel transaction API, replay API, debug hooks, in-kernel transaction entry structure, deallocation records, and the internal replay state when `WAPBL_INTERNAL` is defined.

Kernel transaction API:
- `wapbl_start` attaches a journal to a mount/log vnode with geometry, replay state, and filesystem flush callbacks.
- `wapbl_stop` tears down logging; `wapbl_discard` drops current in-memory transaction state.
- `wapbl_begin`/`wapbl_end` bracket recursive per-thread transactions.
- `wapbl_add_buf`, `wapbl_remove_buf`, and `wapbl_resize_buf` manage metadata buffers captured by the current transaction.
- `wapbl_flush` commits completed transactions and starts asynchronous metadata writes.
- `wapbl_register_inode`/`unregister_inode` track allocated but unlinked inodes for replay cleanup.
- `wapbl_register_deallocation`/`unregister_deallocation` record block revocations.
- Assertion, print/dump, and `wapbl_biodone` hooks support debugging and buffer I/O completion.

Structures and helpers:
- `struct wapbl_entry` tracks one committed transaction's journal pointer, queue entry, unsynced buffer count, reclaimable bytes, and error state.
- `struct wapbl_dealloc` records revoked block address/length.
- `wapbl_vptomp` maps regular or block vnodes to a mount, using `spec_node_getmountedfs` for block devices.
- `wapbl_vphaswapbl` tests whether a vnode's mount has WAPBL enabled.

Replay API:
- Opaque `struct wapbl_replay` is exposed unless internal details are requested.
- `wapbl_replay_start`, `stop`, `free`, `write`, `can_read`, and `read` manage journal replay and read-through from journaled blocks.
- Internal replay state tracks log/device vnodes, block shifts, circular offsets, generation, scratch buffer, block hash, and pending inode list.

Risks and notes:
- Correctness depends on filesystems registering all metadata buffers, deallocations, and unlinked allocated inodes while inside WAPBL transactions.
- Debug macros compile away unless WAPBL debug printing is enabled.
