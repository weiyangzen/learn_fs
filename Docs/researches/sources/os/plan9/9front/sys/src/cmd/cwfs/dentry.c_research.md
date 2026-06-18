# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/dentry.c

Dentry block-address translation, read-ahead, and truncation support.

Important behavior:
- `getdir()` returns a dentry slot inside an `Iobuf`.
- `accessdir()` updates atime/mtime/muid/qid version and respects `Devro` and `noatime`.
- `rel2abs()` resolves relative file block numbers through direct and multi-level indirect pointers, allocating blocks when a target tag is supplied.
- `dnodebuf()` and `dnodebuf1()` fetch data/dir/indirect blocks by relative index.
- `dbufread()` implements simple sequential read-ahead scheduling.
- `dtrunclen()` shrinks files by freeing blocks past the final retained block and zeroing partial tails.
- `dtrunc()` frees all direct and indirect blocks.
