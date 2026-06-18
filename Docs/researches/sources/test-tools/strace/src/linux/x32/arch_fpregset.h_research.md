# sources/test-tools/strace/src/linux/x32/arch_fpregset.h

## Purpose
Reuses the x86_64 floating-point register-set type definition for x32.

## Important APIs, Types, and Functions
Includes `../x86_64/arch_fpregset.h`, which defines `struct_fpregset` with x87 control fields, 64-bit instruction/data pointers, MXCSR fields, `st_space`, `xmm_space`, and padding, and defines `HAVE_ARCH_FPREGSET`.

## Control Flow and Integration
No runtime flow. This header provides the type consumed by `regset.c` and `arch_fpregset.c`.

## State and Persistence
No state; static type metadata only.

## Dependencies
Depends on x86_64 register-set layout and fixed-width integer types.

## Risks
If x32-specific kernel headers ever diverge from x86_64 fpregset layout, the reused type would decode fields incorrectly. Include guards live in the included header.

## Test Signals
Build x32 regset decoding and compare decoded fpregset field offsets against kernel `elf_fpregset_t`/ptrace output.
