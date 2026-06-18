# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/simd.h

This header abstracts SIMD/FPU availability and kernel FPU enter/exit handling for ZFS acceleration code.

Core behavior:
- On x86, `kfpu_initialize()`, `kfpu_init()`, and `kfpu_fini()` are no-op/success macros for this platform.
- In the kernel, `kfpu_allowed()` checks the global `zfs_fpu_enabled` tunable and disables FPU use during panic handling.
- Kernel `kfpu_begin()` uses `KFPU_USE_LWP` for system processes with LWPs, otherwise disables preemption and uses `KFPU_NO_STATE`; `kfpu_end()` mirrors that path.
- Kernel feature predicates query `x86_featureset` for SSE, SSE2, SSE3, SSSE3, AVX, AVX2, AVX512F, and AVX512BW.
- User-level feature predicates query `getisax()` and ISA extension bits.
- Non-x86 builds always disallow kernel FPU support and provide no-op enter/exit stubs.

Risk-sensitive invariants:
- FPU sections must be bracketed by begin/end and cannot run while panic handling.
- AVX/AVX512 feature selection depends on both platform support and the caller respecting `kfpu_allowed()`.
- Non-x86 code paths must tolerate SIMD acceleration being unavailable.
