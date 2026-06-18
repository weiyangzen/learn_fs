# File Research: sources/local-fs/ocfs2-tools/libocfs2/mkjournal.c

Creates and formats OCFS2 journal files and JBD2 journal superblocks.

Journal feature helpers:
- `ocfs2_journal_tag_bytes()` selects 32-bit or 64-bit journal tag size based on `JBD2_FEATURE_INCOMPAT_64BIT`.
- `ocfs2_journal_tag_block()` reconstructs a journal tag block number, including high bits for 64-bit tags.
- `ocfs2_journal_set_features()` and `ocfs2_journal_clear_features()` validate feature masks before mutating the journal superblock.

Feature policy:
- Only JBD2 superblock V2 is supported.
- Unknown compat, ro-compat, or incompat bits are rejected.
- JBD2 checksum compat feature is explicitly rejected because OCFS2 wants journal replay rather than refusing replay after partial checkpointing; OCFS2 relies on metadata ECC for corruption detection.

Endian handling:
- `ocfs2_swap_journal_superblock()` swaps JBD2 big-endian superblock fields on little-endian hosts.

Superblock I/O:
- `ocfs2_init_journal_superblock()` initializes a journal superblock buffer, requires at least 1024 journal blocks, sets block size, first usable journal block, sequence, user count, and filesystem UUID.
- `ocfs2_read_journal_superblock()` checks magic in network order, swaps to CPU, and rejects unsupported features.
- `ocfs2_write_journal_superblock()` swaps to disk order, writes the block, and marks the filesystem changed.

Journal formatting:
- `ocfs2_make_journal()` validates that the target inode is a valid system journal file, grows or truncates it to the requested cluster count, updates size/mtime, and calls `ocfs2_format_journal()`.
- `ocfs2_format_journal()` zeroes the entire journal file in 1 MiB chunks with nocache IO, creates a journal superblock sized to allocated clusters, maps the first file block, and writes the journal superblock there.

Dependencies:
- Uses cached inode I/O, extent mapping, file writes, allocation extension, truncate, byte-order helpers, and low-level IO.
