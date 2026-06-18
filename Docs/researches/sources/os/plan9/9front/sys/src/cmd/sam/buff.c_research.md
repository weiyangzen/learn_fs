# File Research: sources/os/plan9/9front/sys/src/cmd/sam/buff.c

`buff.c` implements sam's text buffer abstraction over temp-file-backed disk blocks. A `Buffer` stores total rune count, an array of `Block*`, and one mutable in-memory cache window.

`setcache` locates and loads the disk block containing a requested position, flushing dirty cached contents first. It preserves append-at-end locality where possible.

`bufinsert` inserts runes by using the current cache if the result fits, allocating new blocks at cache boundaries, or splitting a block when insertion occurs in the middle and the block would overflow `Maxblock`.

`bufdelete` removes a range by repeatedly loading the affected cache block, shifting remaining cache contents left, shrinking the block, and adjusting total rune count. Empty dirty blocks are dropped on flush.

`bufload` reads bytes from a file descriptor, handles partial UTF sequences across reads, converts bytes to runes with `cvttorunes`, elides NULs, and inserts runes into the buffer.

`bufread`, `bufreset`, and `bufclose` provide range reads, destructive reset with block release, and final cleanup.
