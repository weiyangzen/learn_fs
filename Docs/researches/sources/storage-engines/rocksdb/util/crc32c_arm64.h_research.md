# sources/storage-engines/rocksdb/util/crc32c_arm64.h

Purpose: compile-time Arm64 CRC/crypto capability header exposing intrinsics wrappers, prefetch helpers, and Arm CRC function declarations.

Important APIs/macros: defines `HAVE_ARM64_CRC` when building for AArch64 with `__ARM_FEATURE_CRC32`. Maps `crc32c_u8/u16/u32/u64` to ACLE intrinsics. Defines `PREF4X64L1` and `PREF1KL1` assembly prefetch macros. Declares `crc32c_arm64()`, `crc32c_runtime_check()`, and `crc32c_pmull_runtime_check()`. Defines `HAVE_ARM64_CRYPTO` and includes NEON when `__ARM_FEATURE_CRYPTO` is available.

Control flow: the header gates all declarations behind architecture and feature macros, so non-Arm or non-CRC builds see no functions. The prefetch macros expand to `PRFM PLDL1KEEP` assembly.

State and persistence: no state. Its macro decisions control which code paths are compiled and therefore whether stored CRC-compatible values are produced by hardware or fallback code.

Dependencies and integration: included by `crc32c.cc` and `crc32c_arm64.cc`; depends on `<arm_acle.h>` and `<arm_neon.h>` only when relevant.

Risks: compile-time macro detection must match compiler support. Inline assembly constraints are Arm64-specific. Consumers must not call declarations unless the header exposed them under `HAVE_ARM64_CRC`.

Test signals: indirectly covered by `crc32c_test.cc` on Arm64 builds.
