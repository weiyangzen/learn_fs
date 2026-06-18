# File Research: sources/os/plan9/plan9/sys/src/cmd/sam/io.c

Read status: complete, 279 lines.

`io.c` handles `sam` file read/write and terminal startup I/O. `checkqid` warns about multiple open files with the same underlying qid. `writef` writes the addressed range to disk, checking for stale file changes, append-only files, final newline, and updating clean sequence/stat metadata.

`readio` reads from `io` into either an unread file via `bufload` or an existing file through UTF conversion and `loginsert`. It records dev/qid/mtime when requested and warns about NULs. `writeio` converts runes to bytes in blocks and writes them.

`bootterm`, `connectto`, and `startup` set up local or remote `samterm`, using pipes and `rx` for remote execution.

Filesystem relevance: direct file read/write path for `sam`, including stale-file protection, append-only detection, qid tracking, and remote terminal process plumbing.
