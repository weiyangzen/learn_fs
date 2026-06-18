## sources/test-tools/fio/crc/sha3.h

Purpose: SHA-3 constants, context type, and public function declarations.

Important APIs and types: defines digest and block sizes for SHA3-224/256/384/512, `struct fio_sha3_ctx`, digest-specific init functions, `fio_sha3_update()`, and `fio_sha3_final()`.

State and persistence: context contains 25 64-bit lanes, selected digest length/rate, partial buffer, and caller-provided digest output pointer.

Dependencies and integration: includes `<inttypes.h>`, consumed by SHA-3 implementation and checksum users.

Risks and test signals: the fixed buffer is sized to `SHA3_224_BLOCK_SIZE`, the largest SHA-3 rate among supported variants; callers must initialize `sha`. Known NIST vectors should cover all variants.
