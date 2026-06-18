## sources/test-tools/fio/crc/crc32.h

Purpose: declaration header for fio's CRC32 routine.

Important API: `uint32_t fio_crc32(const void * const, unsigned long)` returns the CRC over a caller-provided buffer and length.

State and persistence: no state.

Dependencies and integration: includes `<inttypes.h>` and is included by checksum users and `crc32.c`.

Risks and test signals: header only exposes whole-buffer calculation, not incremental seed/state. Compile coverage and known vectors are the test signals.
