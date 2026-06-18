# File Research: sources/virtualization/spdk/lib/util/crc_internal.h

This private header centralizes CRC acceleration feature selection.

It includes `spdk/config.h`, then chooses one acceleration path: ISA-L headers when `SPDK_CONFIG_ISAL` is set, ARM CRC intrinsics and `SPDK_HAVE_ARM_CRC` on AArch64 with `__ARM_FEATURE_CRC32`, or x86 intrinsics and `SPDK_HAVE_SSE4_2` on x86_64 with `__SSE4_2__`.

CRC implementation files include this header to decide whether to compile ISA-L, ARM hardware, SSE4.2, or table fallback code.
