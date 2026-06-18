# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/include/stat_sysdir.h

## Role

This header declares the system-directory statistics dump function.

## API

`show_stat_sysdir(ocfs2_filesys *fs, FILE *out)` prints the superblock and all objects in the OCFS2 system directory.

## Implementation

The function is implemented in `stat_sysdir.c`.
