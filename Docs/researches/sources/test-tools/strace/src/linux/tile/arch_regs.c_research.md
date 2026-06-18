# sources/test-tools/strace/src/linux/tile/arch_regs.c

## Purpose
Declares the Tile register cache and maps generic register-access macros to Tile's `struct pt_regs` layout. It is included by `syscall.c` to support syscall number, argument, return-value, program-counter, and stack-pointer extraction.

## Important APIs, Types, and Functions
Defines static `struct pt_regs tile_regs`, `ARCH_REGS_FOR_GETREGS tile_regs`, `ARCH_PC_REG tile_regs.pc`, and `ARCH_SP_REG tile_regs.sp`.

## Control Flow and Integration
No functions are defined here. The generic register helpers use `ARCH_REGS_FOR_GETREGS` with ptrace `GETREGS`, then Tile-specific files read or modify `tile_regs`.

## State and Persistence
`tile_regs` is process-global static storage inside the strace process. It is a transient cache refreshed from the current tracee when generic register helpers run; it is not persisted.

## Dependencies
Depends on kernel `struct pt_regs` and the generic `get_regs`, `set_regs`, `get_stack_pointer`, and syscall engine macros. Other Tile files directly share the same `tile_regs` symbol.

## Risks
Because many Tile helpers read this static cache, stale registers can corrupt syscall decoding if `get_regs` was not called on the current tracee before use. `set_regs` writes the whole cached register set back, so callers must avoid preserving stale unrelated fields.

## Test Signals
Tile syscall tracing should show correct PC/SP reporting, syscall arguments, return values, and injected return/error changes. Build-time tests should ensure `struct pt_regs` exposes `pc` and `sp`.
