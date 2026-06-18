# `sources/test-tools/fio/arch/arch-alpha.h`

Purpose: Minimal Alpha architecture support header for fio.

Important APIs: Defines `FIO_ARCH arch_alpha`, `nop` as an empty do-while, `read_barrier()` as `mb`, and `write_barrier()` as `wmb`.

Control flow and integration: Included from `arch.h` when `__alpha__` is defined. Generic fallback paths provide missing optional features such as CPU clock or arch init. `arch.h` also supplies Alpha-specific io_uring syscall numbers.

State and persistence: No state.

Dependencies: Depends on Alpha inline assembly mnemonics and compiler support.

Risks and test signals: Sparse implementation means generic timing and ffz paths must remain valid. Tests require at least cross-compilation for Alpha and, ideally, runtime smoke tests for memory ordering assumptions.
