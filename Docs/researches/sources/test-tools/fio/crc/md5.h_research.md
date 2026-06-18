## sources/test-tools/fio/crc/md5.h

Purpose: MD5 constants, round macros, context type, and public function declarations.

Important APIs and types: defines digest/block/hash sizes, Boolean functions `F1`-`F4`, `MD5STEP`, `struct fio_md5_ctx`, and `fio_md5_init/update/final()`.

State and persistence: context contains a caller-managed `uint32_t *hash`, fixed block buffer, and byte count.

Dependencies and integration: included by `md5.c` and checksum users.

Risks and test signals: pointer-based hash storage is easy to misuse compared with an inline array. Compile-time users and known-answer tests should verify context setup and digest extraction.
