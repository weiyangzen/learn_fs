# File Research: sources/virtualization/nbd/buffer.c

Circular buffer implementation used by the TLS proxy code.

The private `struct buffer` stores a heap buffer, total size, high-water mark, read index, write index, and explicit empty flag. The implementation distinguishes empty from full when `ridx == widx`.

Core APIs allocate/free buffers, expose maximal contiguous read/write spans, mark bytes consumed or produced, test empty/full/high-water state, and compute free/used byte counts.

The implementation is single-threaded and does not perform allocation failure checks. It is designed for event-loop style pumping in `crypto-gnutls.c`, where spans avoid extra copying between plaintext and TLS sides.
