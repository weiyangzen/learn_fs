# sources/test-tools/strace/src/linux/x32/arch_prstatus_regset.h

## Purpose
Reuses x86_64 PRSTATUS register-set structure definitions for x32.

## Important APIs, Types, and Functions
Includes `../x86_64/arch_prstatus_regset.h`, which defines `struct_prstatus_regset` with x86_64 register order and sets `HAVE_ARCH_PRSTATUS_REGSET`.

## Control Flow and Integration
No runtime flow. The header supplies the type for `regset.c` and the architecture decoder.

## State and Persistence
No state.

## Dependencies
Depends on `kernel_ulong_t` sizing and x86_64 register order. The included header delegates to i386 definitions for m32 builds.

## Risks
x32's userspace ABI is ILP32, but ptrace PRSTATUS register layout follows x86_64 register naming/order. Any assumption that `kernel_ulong_t` should be user-long-sized rather than kernel-register-sized is a risk area.

## Test Signals
Compile x32 regset support and compare decoded PRSTATUS offsets against kernel core-note or ptrace regset data.
