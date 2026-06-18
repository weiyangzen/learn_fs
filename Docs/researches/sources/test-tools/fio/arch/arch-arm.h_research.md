# `sources/test-tools/fio/arch/arch-arm.h`

Purpose: Defines fio primitives for 32-bit ARM architectures.

Important APIs: Defines `FIO_ARCH arch_arm`. For ARMv4-v6 variants it uses `mov r0,r0` as `nop` and compiler memory barriers for reads/writes. For ARMv7A/ARMv7VE/ARMv8A it uses `nop` and `__sync_synchronize()` for barriers. Unsupported ARM variants produce a preprocessor error.

Control flow and integration: Selected by `arch.h` for `__arm__`. Generic code uses the defined barrier and nop macros while optional CPU-clock/syscall paths remain absent.

State and persistence: No state.

Dependencies: Relies on compiler-provided ARM architecture macros and inline assembly support.

Risks and test signals: Architecture macro coverage is explicit; newer or differently named ARM targets may fail with `unsupported ARM architecture`. Barrier strength differs between older and newer ARM paths. Tests should cross-compile for representative ARMv5/v6/v7 targets and run concurrency smoke tests on ARMv7+.
