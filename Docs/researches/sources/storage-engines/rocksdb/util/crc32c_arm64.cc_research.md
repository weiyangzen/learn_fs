# sources/storage-engines/rocksdb/util/crc32c_arm64.cc

Purpose: Arm64 CRC-32C hardware implementation and runtime feature probes for CRC32 and PMULL acceleration.

Important APIs/functions: `crc32c_runtime_check()` probes CRC32 instruction support using Linux/FreeBSD auxv, Apple `sysctlbyname`, or OpenBSD CPU ID sysctl. `crc32c_pmull_runtime_check()` similarly checks PMULL/crypto support. `crc32c_arm64(crc, data, len)` computes CRC using Arm CRC intrinsics and optionally a PMULL-assisted 1024-byte parallel path.

Control flow: the file is compiled only under `HAVE_ARM64_CRC`. `crc32c_arm64()` inverts the input CRC, optionally loops over 1024-byte blocks with three parallel lanes and PMULL constants when `pmull_runtime_flag` and `HAVE_ARM64_CRYPTO` are true, then falls back to sequential 8/4/2/1-byte CRC instructions for the tail or for systems without PMULL.

State and persistence: reads external global `pmull_runtime_flag` from `crc32c.cc`, which is set during support checks and dispatch. No persistent storage is written; output must match the generic CRC contract.

Dependencies and integration: depends on `crc32c_arm64.h` for intrinsics/macros, OS feature-probe headers, and Arm NEON/ACLE when enabled. `crc32c.cc` calls this through `ExtendARMImpl()` after `crc32c_runtime_check()`.

Risks: PMULL and CRC32 are separate capabilities; Raspberry Pi-like systems can have CRC32 without PMULL, which this code explicitly handles. It uses unaligned typed pointer loads with sanitizer suppression. Feature probing varies by OS and can return false where support exists but the probing path is unavailable.

Test signals: generic CRC tests exercise this implementation when compiled/run on supported Arm64 hardware; there is no Arm-only unit test in this subset.
