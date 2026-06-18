## sources/test-tools/fio/crc/crc32c.h

Purpose: dispatch header for CRC32C implementations.

Important APIs and flow: declares `crc32c_sw()`, availability globals, optional hardware functions/probes, and inline `fio_crc32c()`. The inline dispatcher checks `crc32c_arm64_available`, then `crc32c_intel_available`, then software fallback. If architecture support is not compiled, hardware names are macro-mapped to `crc32c_sw()` and probes are empty.

State and persistence: external globals hold hardware availability; no local state.

Dependencies and integration: includes fio architecture and type headers. `configure` controls `ARCH_HAVE_CRC_CRYPTO` and `ARCH_HAVE_SSE4_2` availability.

Risks and test signals: callers must ensure probe functions have run before expecting hardware dispatch. Header macro fallback makes builds portable, but can hide missing acceleration. Tests should validate both dispatch state and output equality.
