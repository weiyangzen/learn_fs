# File Research: sources/virtualization/nbdkit/filters/xor/xor.c

This filter applies a reversible XOR transform to data. It supports `xor=VALUE` with `xorlen=1..8`, or `xor=rand[:SEED]`, which uses deterministic pseudo-random 8-byte blocks derived from offset plus seed. Configuration requires exactly one `xor` mode and a valid length, except random mode sets length to 8 and forbids separate `xorlen`.

For value mode, `.get_ready` converts the numeric parameter to big-endian bytes. The data path has optimized aligned loops for 1, 2, 4, and 8 byte patterns and recursive unaligned handling. Random mode locates the generated 64-bit value for each aligned 8-byte window and handles unaligned leading/trailing bytes.

Reads transform the buffer after backend read. Writes copy the caller buffer, transform it, then write the transformed block. Zero and trim are implemented identically by writing transformed zero-filled chunks of up to 64 KiB, preserving FUA only when the backend supports native FUA.

Risks and invariants: trim loses discard/sparse semantics because transformed zero data must be written. Value-mode aligned fast paths cast the `xor` byte array to integer pointers, so byte order and host alignment assumptions matter. Random mode depends on stable `random.c` behavior for reproducibility.
