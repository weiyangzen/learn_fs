# File Research: sources/os/bsd/netbsd-src/lib/libcurses/insdelln.c

Implements line insertion/deletion: `insdelln` and `winsdelln`.

`winsdelln` inserts for positive `nlines` and deletes for negative `nlines`, respecting the window scrolling region when the cursor lies inside it. Parent windows rotate `__LINE` pointers for efficiency, subwindows copy cell contents, cleared lines are filled with the window background, dirty ranges are touched, subwindows are invalidated through `__id_subwins`, and `__sync` propagates changes.
