# File Research: sources/os/bsd/netbsd-src/lib/libc/compiler_rt/Makefile.inc

Read completely: 443 lines.

This makefile fragment integrates LLVM compiler-rt builtins and profiling runtime sources into NetBSD libc. It selects CPU/architecture-specific source directories, conditionally adds integer arithmetic, overflow-checking, soft/hard floating-point, complex, quad-precision, cache flush, ARM AEABI, PowerPC, aarch64, and profiling sources, then chooses assembly overrides when present.

Important interactions: adapts upstream compiler-rt source selection to NetBSD libc architecture policy and build flags. It adds many per-source lint suppressions and includes `${COMPILER_RT_DIR}/abi.mk`.

Security/reliability notes: build-only but critical for low-level compiler helper availability. Incorrect architecture conditions can cause missing builtins or ABI-incompatible helper implementations.
