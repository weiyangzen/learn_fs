# sources/test-tools/strace/src/linux/tile/userent.h

## Purpose
Defines Tile ptrace user-register offset names for `PTRACE_PEEKUSER` and related decoding.

## Important APIs, Types, and Functions
Provides table rows mapping `PTREGS_OFFSET_REG(0)` through `PTREGS_OFFSET_REG(52)` to `r0` through `r52`, plus named offsets for `tp`, `sp`, `lr`, `pc`, `ex1`, `faultnum`, `orig_r0`, and `flags`.

## Control Flow and Integration
No runtime control flow. Included by `ptrace.c` table machinery so numeric user-area offsets can be printed as Tile register names.

## State and Persistence
No state. The compiled offset table is static metadata.

## Dependencies
Depends on Tile `PTREGS_OFFSET_*` macros from kernel headers or generated architecture definitions and on the including xlat/table context.

## Risks
Register offset macros must match the kernel `pt_regs` layout. Incorrect mappings affect ptrace offset display and can mislead users debugging register access.

## Test Signals
Ptrace decoder tests should verify representative offsets for argument registers, stack pointer, program counter, original return register, and flags.
