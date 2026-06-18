# File Research: sources/local-fs/erofs-utils/lib/liberofs_xxhash.h

This header wraps xxHash support.

Behavior:
- If system xxhash headers/library are available, `xxh32()` and `xxh64()` inline to `XXH32()` and `XXH64()`.
- Otherwise it declares local fallback implementations:
  - `uint32_t xxh32(const void *input, size_t length, uint32_t seed)`
  - `uint64_t xxh64(const void *input, const size_t len, const uint64_t seed)`

It uses a dual BSD-2-Clause/GPL-2.0+ license and C++ extern guards.

Risk / note:
- The wrapper intentionally exposes the same local function names regardless of backend; consumers should include this header rather than directly depending on system xxhash.
