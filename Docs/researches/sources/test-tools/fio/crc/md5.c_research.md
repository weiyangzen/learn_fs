## sources/test-tools/fio/crc/md5.c

Purpose: MD5 implementation adapted from Linux kernel crypto code for fio checksums.

Important APIs and flow: `fio_md5_init()` initializes the four hash words, `fio_md5_update()` accumulates data into 64-byte blocks and calls `md5_transform()`, and `fio_md5_final()` appends MD5 padding/bit length and transforms the final block. `md5_transform()` performs all four MD5 rounds via macros from the header.

State and persistence: state lives in caller-owned `struct fio_md5_ctx`: hash storage pointer, 16-word block buffer, and byte count. No persistent files.

Dependencies and integration: depends on `md5.h` for context and round macros. Used by fio verification/checksum code and CRC/hash test harness.

Risks and test signals: `struct fio_md5_ctx` stores `hash` as a pointer, so callers must provide valid backing storage before init/update/final. Finalization writes digest words in context state rather than returning bytes. Known MD5 vectors and memory-safety tests around context allocation are the key signals.
