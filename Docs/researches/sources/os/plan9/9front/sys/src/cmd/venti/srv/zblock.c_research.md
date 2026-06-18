# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/zblock.c

`zblock.c` implements aligned variable-sized `ZBlock` buffers. `alloczblock()` allocates raw memory, aligns the data pointer to the requested block size, places the `ZBlock` descriptor after the data, optionally zeroes data, and writes an overflow sentinel after the logical data region.

`freezblock()` checks the sentinel before freeing, catching overwrites past `b->_size`. Helpers convert between `Packet` and `ZBlock`, and `fmtzbinit()` initializes a `Fmt` to write into a `ZBlock`.

This is a core buffer abstraction for disk blocks, config serialization, clump data, and utility I/O.
