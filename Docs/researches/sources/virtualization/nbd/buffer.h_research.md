# File Research: sources/virtualization/nbd/buffer.h

Public interface for the circular buffer used by TLS proxying.

It declares opaque `buffer_t` and the allocation, span, completion, state, free-space, and count functions implemented in `buffer.c`.

The header carries an MIT license block from Wrymouth Innovation Ltd and uses `ssize_t`, so it includes `stdlib.h` and `sys/types.h`.
