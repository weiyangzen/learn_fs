# `sources/test-tools/fio/arch/arch-ppc.h`

Purpose: Provides PowerPC/PowerPC64 fio architecture primitives for barriers, bit operations, and optional CPU clock.

Important APIs: Defines `FIO_ARCH arch_ppc`, `__SANE_USERSPACE_TYPES__`, `read_barrier()` as `lwsync` on ppc64 or `sync` otherwise, `write_barrier()` as `sync`, `arch_ffz()` using count-leading-zero instructions, `mfspr()`, and `get_cpu_clock()` from time-base registers. For ppc64, `ARCH_HAVE_CPU_CLOCK` is enabled; for non-ppc64 it is disabled despite implementation. `arch_init()` currently returns 0 with disabled alternate timebase probing.

Control flow and integration: Selected by `arch.h` for PowerPC macros. Generic code can use `ARCH_HAVE_FFZ` and, on ppc64, CPU clock support.

State and persistence: Disabled code could set `arch_flags` and `tsc_reliable`; active init does not mutate state.

Dependencies: PowerPC inline assembly, `BITS_PER_LONG`, SPR register semantics, and external `arch_flags`/`tsc_reliable` declarations.

Risks and test signals: Non-ppc64 CPU clock is implemented but intentionally not advertised; changing this requires care. The ppc64 clock loop waits for nonzero TBRL and may be platform-sensitive. Tests should build ppc32/ppc64, validate ffz, and run timing/rate workloads on ppc64.
