# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/auxv.h

This header defines illumos auxiliary vector types and common auxiliary vector constants used around `exec`, runtime linker startup, brands, hardware capability reporting, and secure execution flags.

Key contents:
- `auxv_t` with `a_type` plus value/pointer/function union.
- `auxv32_t` under `_SYSCALL32`.
- Standard ELF auxiliary vector constants `AT_NULL` through `AT_ENTRY`.
- Commentary on PPC/Linux/LSB auxiliary vector values that illumos mostly does not emit.
- Sun extensions `AT_SUN_*` for uid/gid, runtime linker metadata, platform, hardware capabilities, icache flush, CPU/MMU names, exec path, aux flags, emulator/brand data, commpage, x86 FPU type/size.
- Kernel globals for `auxv_hwcap`, `auxv_hwcap_2`, `auxv_hwcap_3`, and 32-bit equivalents.
- User declaration for `getisax()`.
- `AF_SUN_*` flags for secure linker behavior, hardware-cap verification, and primary link-map behavior.
- Includes arch-specific `auxv_SPARC.h` and `auxv_386.h` depending on target macros or compiler architecture.

Dependencies:
- Includes `sys/types.h`.
- C++ guarded with `extern "C"`.

Research notes:
- This is ABI-facing and shared by kernel, libc/runtime linker, and userland.
- The architecture-specific hardware capability namespaces are intentionally factored into separate headers.
