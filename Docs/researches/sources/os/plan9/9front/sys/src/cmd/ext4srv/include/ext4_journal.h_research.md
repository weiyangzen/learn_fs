# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_journal.h

Runtime JBD journal data structures and API header.

Key behavior:
- `jbd_fs` binds a journal inode reference, journal superblock, block device, UUID checksum seed, and dirty flag.
- `jbd_buf` tracks one journaled copy of a filesystem block and links into transaction and per-block dirty queues.
- `jbd_revoke_rec` and `jbd_block_rec` are red-black-tree records for revoked LBAs and live block ownership.
- `jbd_trans` stores transaction ID, journal block allocation state, data/write counters, checksum/error fields, owning journal, buffer queue, revoke tree, block record list, and checkpoint queue node.
- `jbd_journal` stores active log pointers, transaction IDs, block size, checkpoint queue, live block record tree, and owning JBD filesystem.
- Declares journal load/unload, inode block mapping, recovery, start/stop, transaction allocation, dirty marking, revoke handling, transaction free/commit, and checkpoint purge.

Notable dependencies:
- Includes `queue.h` and `tree.h`; on-disk JBD structs come from `ext4_types.h`.
- Implemented by `ext4_journal.c`; used by `ext4.c` and `ext4_trans.c`.

Research notes:
- Live transaction ownership is per filesystem LBA, allowing later transactions to supersede earlier dirty buffers during checkpointing.
