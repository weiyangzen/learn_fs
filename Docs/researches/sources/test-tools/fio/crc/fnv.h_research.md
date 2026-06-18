## sources/test-tools/fio/crc/fnv.h

Purpose: declaration header for the 64-bit FNV helper.

Important API: `uint64_t fnv(const void *, uint32_t, uint64_t)` accepts data, length, and initial/current hash value.

State and persistence: no state.

Dependencies and integration: includes `<inttypes.h>` and is consumed by checksum/hash callers.

Risks and test signals: header does not define an initial constant, so callers must choose the intended seed. Compile and known-answer hash tests validate usage.
