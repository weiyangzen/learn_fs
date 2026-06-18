## sources/test-tools/fio/crc/crc32.c

Purpose: POSIX-style CRC32/checksum implementation using a static 256-entry table.

Important API and flow: `fio_crc32(const void *buffer, unsigned long length)` initializes `crc` to zero, then for each byte shifts left and xors the table entry indexed by the high CRC byte mixed with input.

State and persistence: no mutable state; table is file-local constant data.

Dependencies and integration: depends on `crc32.h` and standard integer types. Used by verification/checksum selection and CRC tests.

Risks and test signals: this is not the same variant as CRC32C and uses a zero initial value; incorrect caller expectations would produce mismatches. Known-answer tests and benchmark comparisons in the CRC test harness are the main signal.
