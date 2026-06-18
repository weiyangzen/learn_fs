## sources/test-tools/fio/crc/sha3.c

Purpose: SHA-3/Keccak implementation supporting SHA3-224, SHA3-256, SHA3-384, and SHA3-512.

Important APIs and flow: digest-specific init functions call `fio_sha3_init()` with the digest size, setting rate (`rsiz`) and zeroing state/buffer. `fio_sha3_update()` absorbs full rate-sized blocks by xoring little-endian words into the 25-lane state and running `keccakf()`. `fio_sha3_final()` applies SHA-3 domain padding (`0x06` and final `0x80`), runs one final permutation, converts state lanes to little endian, and copies `md_len` bytes to `sctx->sha`. `keccakf()` implements the 24 rounds of Theta, Rho/Pi, Chi, and Iota.

State and persistence: caller-owned context stores state lanes, digest size, rate, partial byte count, staging buffer, and output pointer `sha`.

Dependencies and integration: includes `../os/os.h` for `cpu_to_le64()` and `sha3.h`. Used by fio checksum/verification and CRC/hash tests.

Risks and test signals: context output pointer must be initialized by caller. The code casts buffers to `uint64_t *`, so alignment and endian behavior matter. Known SHA-3 vectors for all four digest sizes and sanitizer builds validate this path.
