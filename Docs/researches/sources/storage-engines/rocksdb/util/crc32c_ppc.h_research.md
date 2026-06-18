# sources/storage-engines/rocksdb/util/crc32c_ppc.h

Purpose: C/C++ ABI declaration for the PowerPC CRC-32C implementation.

Important API: declares `uint32_t crc32c_ppc(uint32_t crc, unsigned char const* buffer, size_t len)`, wrapped in `extern "C"` for C++ callers.

Control flow: none; this is a declaration-only header.

State and persistence: no state. The function's output participates in persistent checksum compatibility through `crc32c.cc` dispatch.

Dependencies and integration: includes `<cstddef>` and `<cstdint>`. Used by `crc32c.cc` and implemented by `crc32c_ppc.c`.

Risks: callers rely on build-time/runtime gates to avoid calling the stub implementation on unsupported targets.

Test signals: indirectly covered by CRC tests on PPC-capable builds.
