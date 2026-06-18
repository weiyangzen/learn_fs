# File Research: sources/os/plan9/plan9/sys/src/cmd/sam/buff.c

Read status: complete, 302 lines.

`buff.c` implements `sam`’s block-based rune buffer on top of a temporary disk store. A `Buffer` maintains block pointers plus a cached block that is flushed to disk when dirty or empty.

`bufinsert` inserts runes, growing or splitting blocks as needed. `bufdelete` removes ranges. `bufload` reads bytes from a file descriptor, converts UTF to runes while handling partial runes and NULs, and inserts into the buffer. `bufread`, `bufreset`, and `bufclose` provide range reads and cleanup.

The implementation avoids keeping whole edited files in contiguous memory and uses `Maxblock`-sized chunks backed by `disk.c`.

Filesystem relevance: core editor storage layer for file contents, backed by a temporary file.
