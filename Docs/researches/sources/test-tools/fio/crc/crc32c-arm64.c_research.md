## sources/test-tools/fio/crc/crc32c-arm64.c

Purpose: ARMv8 CRC/crypto accelerated CRC32C implementation with runtime feature probing.

Important APIs and flow: defines global `crc32c_arm64_available`, `crc32c_arm64()` when `ARCH_HAVE_CRC_CRYPTO` is compiled, and `crc32c_arm64_probe()`. The accelerated path processes 1024-byte blocks using ARM CRC intrinsics and PMULL folding constants, then handles remaining 64/32/16/8-bit pieces. The probe uses `os_cpu_has(CPU_ARM64_CRC32C)` once.

State and persistence: mutable globals `crc32c_arm64_available` and private `crc32c_probed` cache CPU capability. No persistent files.

Dependencies and integration: depends on `crc32c.h`, `os_cpu_has`, `<arm_acle.h>`, and `<arm_neon.h>`. `fio_crc32c()` in the header dispatches here before Intel and software paths when available.

Risks and test signals: unaligned casts and architecture-specific intrinsics require correct compiler flags from `configure` (`ARCH_HAVE_CRC_CRYPTO`). Runtime probing must match execution CPU. CRC32C known-answer tests must be run on capable ARM64 hardware and compared with `crc32c_sw()`.
