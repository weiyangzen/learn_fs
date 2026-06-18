# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/auxv_386.h

This header defines x86-specific `AT_SUN_HWCAP`, `AT_SUN_HWCAP2`, `AT_SUN_HWCAP3`, and `AT_SUN_FPTYPE` bit values.

Key contents:
- `AV_386_*` HWCAP bits for baseline x87/i386 features through SSE, AVX, VMX, SVM, AES, PCLMULQDQ, POPCNT, etc.
- `FMT_AV_386` printf/bit-format string.
- `AV_386_2_*` HWCAP2 bits for F16C, RDRAND, BMI, FMA, AVX2, ADX, RDSEED, AVX-512 families, SHA, FSGSBASE, CLWB, VAES, GFNI, etc.
- `FMT_AV_386_2`.
- `AV_386_3_*` HWCAP3 bits for AVX512 VBMI2 and BF16.
- `FMT_AV_386_3`.
- `AT_386_FPINFO_*` values describing FPU save layout: none, FXSAVE, XSAVE, XSAVE_AMD.

Dependencies:
- Intended to be included by `sys/auxv.h`.
- C++ guarded with `extern "C"`.

Research notes:
- Bit assignments are externally meaningful to runtime linker/libc consumers.
- Comments note withdrawn bit positions and unsupported `xsavec`.
