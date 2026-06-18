# sources/test-tools/strace/src/linux/x32/arch_regs.h

## Purpose
Reuses x86_64 register index constants for x32.

## Important APIs, Types, and Functions
Includes `../x86_64/arch_regs.h`, which defines indices such as `R15`, `RAX`, `ORIG_RAX`, `RIP`, `RSP`, `FS_BASE`, and `GS` for register-array based ptrace access.

## Control Flow and Integration
No runtime flow. Included by `regs.h` and syscall/register helpers that need portable symbolic offsets.

## State and Persistence
No state.

## Dependencies
Depends on x86_64 kernel ptrace register ordering.

## Risks
Wrong register indices would affect raw register access and syscall mutation. The x32 target depends on x86_64 register order despite ILP32 userspace.

## Test Signals
Register access tests should verify `ORIG_RAX`, `RAX`, `RIP`, and `RSP` indices under x32.
