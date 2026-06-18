## sources/test-tools/fio/crc/sha1.c

Purpose: SHA-1 implementation based on Mozilla code, optimized to avoid extra context copies.

Important APIs and flow: `fio_sha1_init()` initializes five state words and size. `fio_sha1_update()` appends input into the 64-byte/16-word working buffer and calls `blk_SHA1Block()` for complete blocks. `fio_sha1_final()` appends SHA-1 padding and big-endian length using `htonl()`. `blk_SHA1Block()` performs all 80 rounds using rolling 16-word schedule macros and x86 rotate assembly where available.

State and persistence: state is caller-owned `struct fio_sha1_ctx`: state pointer `H`, working buffer `W`, and total size. No files.

Dependencies and integration: depends on `<arpa/inet.h>` and `sha1.h`. Used by fio verification/checksum and CRC/hash tests.

Risks and test signals: `H` is a pointer requiring valid external storage; update does pointer arithmetic on `void *`, relying on compiler extension behavior. Known SHA-1 vectors and sanitizer builds should validate context setup and padding.
