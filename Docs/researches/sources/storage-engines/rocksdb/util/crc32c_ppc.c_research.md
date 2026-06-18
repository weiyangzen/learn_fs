# sources/storage-engines/rocksdb/util/crc32c_ppc.c

Purpose: C wrapper around the Power8 VPMSUM assembly CRC implementation, with scalar alignment/tail handling and a no-op stub for unsupported builds.

Important APIs/functions: `crc32c_ppc(crc, data, len)` is the exported C ABI. Under `HAVE_POWER8`, `crc32_vpmsum()` handles CRC inversion, 16-byte alignment, assembly call to `__crc32_vpmsum()`, and tail bytes using `crc32_align()`. Under non-Power8 builds, `crc32c_ppc()` exists but returns zero and is not expected to be called.

Control flow: short or unaligned prefixes are processed by table-driven `crc32_align()`. Aligned bulk data is passed to assembly in 16-byte multiples. Tail bytes are processed after assembly. A `NULL` data pointer triggers temporary zero-filled allocation before calculating CRC, a compatibility workaround for assembly behavior.

State and persistence: no retained state. Results must match standard CRC-32C with configured `CRC_XOR` and reflected constants from `crc32c_ppc_constants.h`.

Dependencies and integration: includes `crc32c_ppc_constants.h` with `CRC_TABLE` for scalar fallback constants. Called from `crc32c.cc` through `ExtendPPCImpl()` when Power8/AltiVec feature probing succeeds.

Risks: the unsupported stub returns an invalid checksum if accidentally called. The `NULL` workaround allocates `len` bytes and can be expensive or fail for large lengths. Correctness depends on pointer alignment, endian/reflection macros, and the assembly symbol matching the C declaration.

Test signals: generic CRC tests cover it on Power8 builds. No explicit allocation-failure or null-input test is present in this subset.
