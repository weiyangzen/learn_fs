# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/journal.c

## Role

`journal.c` reads an OCFS2 journal inode and decodes its contents for `logdump`.

## Flow

`read_journal()` opens the journal inode as a cached inode, allocates a journal superblock buffer and a 1 MiB read buffer, reads the journal file sequentially, dumps the journal superblock from block 0, then scans remaining blocks.

`scan_journal()` distinguishes JBD2 blocks by magic number, known OCFS2 metadata blocks by `ocfs2_detect_block()`, and unknown ranges as probable data.

## Output

It delegates JBD2 block formatting, OCFS2 metadata formatting, and unknown-range reporting to `dump.c`.

## Risk Areas

The code reads sequentially and decodes journal contents as present, not as a replay engine. It depends on current block size and byte-order interpretation matching the journal format.
