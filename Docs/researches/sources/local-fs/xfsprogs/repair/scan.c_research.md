# File Research: sources/local-fs/xfsprogs/repair/scan.c

Implements phase scanning of allocation groups, on-disk btrees, AG headers, block ownership maps, inode btrees, rmap/refcount btrees, realtime metadata btrees, and global counter validation.

Key structures:
- `struct aghdr_cnts`: per-AG manual counters for AGF/AGI and superblock validation.
- `struct rmap_priv`: scanner state for rmap btree high-key/last-record validation.
- `struct refc_priv`: scanner state for refcount btree validation.
- `struct ino_priv`: inode and free-inode btree scan accounting.

Core traversal:
- `salvage_buffer` reads buffers even after verifier failure, producing zeroed suspect buffers on EIO.
- `scan_sbtree` walks short-form AG btrees by AG block number.
- `scan_lbtree` walks long-form inode-hosted btrees by fsblock and handles dirty CRC/key repairs.
- `scan_bmapbt` validates inode bmap btrees, sibling links, owner/blkno/uuid, key ordering, extents, duplicate claims, and optionally records bmbt rmaps.

AG metadata scans:
- `scan_allocbt` validates bnobt/cntbt records, free-space ordering, block ownership states, and free-block counters.
- `scan_rmapbt` validates AG rmapbt records, ordering, owners, impossible field combinations, high keys, merge opportunities, and block-owner consistency.
- `scan_refcbt` validates AG refcountbt records, CoW/shared domains, counts, ordering, merge opportunities, and block claims.
- `scan_freelist` walks AGFL entries and marks them free.
- `validate_agf` drives bnobt/cntbt/rmapbt/refcountbt scans and compares counted fields against AGF values.
- `validate_agi` drives inobt/finobt scans, checks block counts, inode counts, free counts, and unlinked buckets.

Realtime metadata scans:
- `process_rtrmap_reclist` and `scan_rtrmapbt` validate realtime rmap records and inode-hosted rtrmap btrees.
- `process_rtrefc_reclist` and `scan_rtrefcbt` validate realtime refcount records and inode-hosted rtrefcount btrees.
- Suspect realtime rmap/refcount trees call the same avoid-check paths as AG trees.

Inode btree logic:
- `verify_single_ino_chunk_align` validates inode chunk alignment and agino range.
- `import_single_ino_chunk` imports certain records into in-core inode trees or uncertain records when suspect.
- `scan_single_ino_chunk` handles allocation inobt records and marks inode blocks.
- `scan_single_finobt_chunk` cross-checks finobt against inobt-derived in-core state.
- `scan_inobt` walks inobt/finobt blocks and records bad inode btree state if corruption is detected.

Top-level:
- `scan_ag` reads SB/AGF/AGI, repairs AG headers when allowed, scans all AG structures, writes corrected headers/CRCs, and updates progress.
- `scan_ags` runs AG scans through the workqueue, aggregates counters, and compares them to superblock summary counters.

Important behavior:
- Scanner is intentionally salvage-oriented: it keeps walking suspect trees until consecutive corruption makes traversal unsafe.
- Block map states distinguish unknown, free, inode, fs metadata, rmap-observed, refcount, CoW, metadata-file, duplicate, and in-use states.
- Rmap/refcount corruption sets avoid flags so later phases rebuild instead of trusting old btrees.
