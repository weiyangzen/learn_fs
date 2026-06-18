## sources/test-tools/fio/crc/sha1.h

Purpose: SHA-1 context and function declarations.

Important APIs and types: `struct fio_sha1_ctx` contains `uint32_t *H`, `unsigned int W[16]`, and byte `size`; functions are `fio_sha1_init()`, `fio_sha1_update()`, and `fio_sha1_final()`.

State and persistence: all hash state is caller-owned. No persistence.

Dependencies and integration: includes `<inttypes.h>` and is consumed by checksum code and `sha1.c`.

Risks and test signals: pointer-backed `H` requires correct caller allocation. Compile plus known SHA-1 vectors validate the interface.
