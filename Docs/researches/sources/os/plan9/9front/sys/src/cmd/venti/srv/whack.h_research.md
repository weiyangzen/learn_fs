# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/whack.h

`whack.h` defines the shared compressor/decompressor state and constants for Venti’s whack format. It sets stats count, error string length, maximum match offset, hash table size, minimum match length, decode threshold, and sequence-mask constants.

`Whack` stores the rolling hash table, back-link ring, start time, and source pointer. `Unwhack` stores the latest error message. The header declares initialization, compression, decompression, and one-shot block compression APIs.
