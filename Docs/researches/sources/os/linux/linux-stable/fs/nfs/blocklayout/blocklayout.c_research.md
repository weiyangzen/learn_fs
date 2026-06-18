# File Research: sources/os/linux/linux-stable/fs/nfs/blocklayout/blocklayout.c

Implements the NFSv4.1 pNFS block and SCSI layout driver core.

Key behavior:
- Registers two layout drivers: `LAYOUT_BLOCK_VOLUME` and `LAYOUT_SCSI`.
- Translates NFS layout extents into block-device BIO reads/writes.
- `parallel_io` tracks multiple bios for one NFS page I/O header and calls the pNFS completion callback only after the final bio completes.
- Read path looks up extents, submits bios for data extents, zero-fills holes, updates EOF/count, and falls back through pNFS error handling on failures.
- Write path writes whole pages, marks extents written for layoutcommit, and reports `NFS_FILE_SYNC`.
- BIO errors mark layout segment failure and mark affected deviceids unavailable.
- Layout segment allocation decodes XDR extents, resolves/registers deviceids, verifies extent ordering/COW constraints, then inserts extents into the layout extent tree.
- Layout return removes affected extents from read/write trees.
- Pageio ops enforce sector/page alignment and reset to MDS I/O when block layout cannot handle a request.
- `set_layoutdriver()` rejects missing or page-larger server block sizes.
- Module init initializes pipefs support and registers block then SCSI drivers; exit unregisters both and cleans pipefs.

Important constraints:
- Reads require sector alignment for direct I/O.
- Writes require page alignment, except EOF direct writes can write full zero-padded pages per RFC behavior.
- Extent verification rejects invalid read/write/COW coverage combinations before extents become active.
