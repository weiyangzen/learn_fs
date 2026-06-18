# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfarc4.c

Implements PostScript filter operators for the Arcfour cipher stream used by PDF encryption.

`ArcfourDecode` and `ArcfourEncode` both read a parameter dictionary, require a `Key` entry, initialize `stream_arcfour_state` with `s_arcfour_set_key()`, and create the corresponding read or write filter.

Because Arcfour is symmetric, encode and decode differ only in using `filter_write()` versus `filter_read()`.

The filter state is allocated in the stream memory pool rather than the key object's VM space because the state keeps no pointers.

Registered as filter operators in `zfarc4_op_defs`.
