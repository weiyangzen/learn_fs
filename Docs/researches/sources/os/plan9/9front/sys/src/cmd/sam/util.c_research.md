# File Research: sources/os/plan9/9front/sys/src/cmd/sam/util.c

`util.c` contains small shared helpers for rune conversion, temporary buffers, and unsigned min.

`cvttorunes` converts a byte buffer to runes, assuming the caller provided enough trailing bytes to avoid partial-rune ambiguity. It elides NUL runes and optionally reports that NULs were seen.

`fbufalloc` and `fbuffree` allocate/free fixed-size file buffers using sam's panic-on-failure allocator.

`min` returns the smaller of two unsigned integers and is used in buffer and window logic.
