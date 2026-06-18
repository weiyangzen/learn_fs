# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/pass4.c

Purpose: implements fsck pass 4, replaying orphan directories and reconciling inode link counts with directory-entry reference counts.

Read coverage: complete file read, 371 lines.

Key responsibilities:
- Pass 4a iterates all slot orphan directories, truncating orphan inode contents, deleting normal orphan inodes, and clearing orphan dirents.
- Preserves DIO orphan inodes from deletion while still truncating their orphaned state.
- Creates missing orphan directories during normal pass 4 when they are absent, commonly after failed slot removal.
- Updates in-memory inode/link reference accounting when orphan entries are replayed during a forced check.
- Pass 4b walks the union of inodes seen in directory references and in inode link counts, reconnecting unreferenced inodes to `/lost+found` and correcting `i_links_count`.

Important entry points:
- `o2fsck_pass4()` runs orphan replay and link-count reconciliation.
- `replay_orphan_dir()` is shared by pass 4 and slot recovery.
- `replay_orphan_iterate()` handles each orphan dirent.
- `create_orphan_dir()` recreates missing slot orphan dirs.
- `check_link_counts()` compares `ost_icount_refs` and `ost_icount_in_inodes`.
- `next_inode_any_ref()` merges iteration over both icount maps.

Dependencies:
- Uses pass 3 reconnection, inode-count maps, libocfs2 orphan directory naming, lookup, dir iteration, truncate, delete inode, new system inode, init dir, link, and inode write APIs.

Risk and edge cases:
- In read-only/no-write mode, orphan replay is skipped and directory iteration aborts.
- During slot recovery, orphan directory errors are returned to force a full check; during pass 4, missing orphan dirs can be repaired.
- Orphaned directories affect both child and parent link counts, so replay has type-specific icount deltas.
- Link-count repair depends on pass 2 having cleared invalid directory references.
