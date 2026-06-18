# File Research: sources/os/bsd/netbsd-src/sys/sys/wapbl_replay.h

Read completely: 150 lines.

Defines the on-disk WAPBL journal record layout used by replay. This is the persistent ABI for WAPBL headers, block lists, revocations, and unlinked inode lists.

Journal layout:
- A journal header precedes a circular data region.
- `wc_head` and `wc_tail` are byte offsets from the start of the journal header; both zero means empty, equal nonzero means full.
- Records are tagged with a 32-bit type and length and padded to log device block boundaries.

Record types:
- `WAPBL_WC_HEADER` (`"WABL"`) identifies `struct wapbl_wc_header`.
- `WAPBL_WC_BLOCKS` and `WAPBL_WC_REVOCATIONS` share `struct wapbl_wc_blocklist`.
- `WAPBL_WC_INODES` uses `struct wapbl_wc_inodelist`.

Structures:
- `struct wapbl_wc_header` stores checksum, generation, fsid, timestamp, version, log/fs block shifts, circular head/tail/off/size, and spare payload.
- `struct wapbl_wc_blocklist` stores count plus variable-length block descriptors with disk address and length; block records are followed by logged block data, while revocation records carry no data.
- `struct wapbl_wc_inodelist` stores variable-length inode number/mode pairs and a clear flag to supersede previous inode lists.

Risks and notes:
- Replay safety depends on handling revocations before stale logged data can overwrite blocks reallocated as data.
- Variable-length trailing arrays and on-disk padding require careful length validation when parsing damaged journals.
