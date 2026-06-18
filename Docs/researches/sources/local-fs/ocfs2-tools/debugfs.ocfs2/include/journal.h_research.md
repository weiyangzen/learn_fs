# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/include/journal.h

## Role

This header exposes journal-reading support for `debugfs.ocfs2`.

## API

It declares `read_journal(ocfs2_filesys *fs, uint64_t blkno, FILE *out)`, which reads a journal inode and prints decoded JBD2 and OCFS2 metadata contents.

## Implementation

The function is implemented in `journal.c`.
