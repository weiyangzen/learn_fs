# File Research: sources/local-fs/ocfs2-tools/libocfs2/dir_iterate.h

Private header for directory iteration.

Defines `struct dir_context`, carrying the target directory block number, flags, saved dinode, working block buffer, callback, private data, and callback error code. Declares `ocfs2_process_dir_block()`, the block-iterator callback shared with `dir_iterate.c`.

Also defines directory-entry alignment constants and `OCFS2_DIR_REC_LEN(name_len)`, which rounds a dirent record length to the OCFS2 4-byte directory padding boundary.
