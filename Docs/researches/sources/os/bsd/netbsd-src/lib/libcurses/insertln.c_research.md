# File Research: sources/os/bsd/netbsd-src/lib/libcurses/insertln.c

Implements insert-line convenience APIs: `insertln` and `winsertln`.

Both are thin wrappers over `winsdelln(..., 1)`, preserving the cursor while inserting one blank line at the current line using the full line insertion engine in `insdelln.c`.
