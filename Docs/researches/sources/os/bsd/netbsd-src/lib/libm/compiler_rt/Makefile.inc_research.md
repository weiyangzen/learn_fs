# File Research: sources/os/bsd/netbsd-src/lib/libm/compiler_rt/Makefile.inc

## Scope

Build integration for compiler-rt complex arithmetic builtins inside NetBSD libm.

## APIs And Behavior

- Sets `COMPILER_RT_DIR` and source directories under `sys/external/bsd/compiler_rt/dist`.
- Uses special `ppc` directory mapping for `MACHINE_CPU == powerpc`; otherwise uses `${MACHINE_CPU}` and `${MACHINE_ARCH}`.
- Adds generic complex multiply/divide builtins for `float`, `double`, and extended precision (`mulsc3`, `muldc3`, `mulxc3`, `divsc3`, `divdc3`, `divxc3`).
- Adds `divtc3` and `multc3` for powerpc, sparc64, and aarch64.
- Chooses assembly implementation if a CPU/arch `.S` exists; otherwise compiles C with `-Wno-error=missing-prototypes`.
- Includes compiler-rt ABI definitions.

## Dependencies And Risks

- Depends on compiler-rt source tree layout and NetBSD make conditionals.
- Architecture-specific assembly selection is path-existence driven.
