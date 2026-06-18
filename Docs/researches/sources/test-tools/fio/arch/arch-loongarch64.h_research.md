# `sources/test-tools/fio/arch/arch-loongarch64.h`

Purpose: Minimal LoongArch64 architecture support for fio.

Important APIs: Defines `FIO_ARCH arch_loongarch64`, read/write barriers as `dbar 0`, and `nop` also as `dbar 0`.

Control flow and integration: Selected by `arch.h` when `__loongarch64` is defined. Optional CPU-clock, syscall, and ffz hooks are absent, so generic paths apply.

State and persistence: No state.

Dependencies: LoongArch inline assembly support.

Risks and test signals: Using a full barrier as `nop` may be conservative but expensive. Missing CPU clock support can affect timing fast paths. Tests should cross-compile and run basic I/O/rate workloads on LoongArch64.
