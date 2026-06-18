## sources/test-tools/fio/crc/murmur3.h

Purpose: declaration header for fio's MurmurHash3 helper.

Important API: `uint32_t murmurhash3(const void *key, uint32_t len, uint32_t seed)`.

State and persistence: no state; caller supplies seed.

Dependencies and integration: includes `<inttypes.h>` and is used by hash callers/tests.

Risks and test signals: header gives no endian/alignment caveats, so tests should cover architectures used by fio. Known-answer vectors validate behavior.
