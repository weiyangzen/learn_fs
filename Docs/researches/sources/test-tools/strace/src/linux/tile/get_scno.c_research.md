# sources/test-tools/strace/src/linux/tile/get_scno.c

## Purpose
Extracts Tile syscall number and selects the current strace personality.

## Important APIs, Types, and Functions
Defines `arch_get_scno(struct tcb *tcp)`. It computes `currpers`, calls `update_personality(tcp, currpers)`, assigns `tcp->scno = tile_regs.regs[10]`, and returns `1`.

## Control Flow and Integration
On `__tilepro__`, the function always selects personality 1. Otherwise it checks `tile_regs.flags & PT_FLAGS_COMPAT`, defining `PT_FLAGS_COMPAT 0x10000` locally if old headers lack it, and selects personality 1 for compat or 0 for native. Generic `get_scno` then uses `tcp->scno` to index the active syscall table.

## State and Persistence
Mutates per-tracee fields through `update_personality` and `tcp->scno`. Reads the transient `tile_regs` cache.

## Dependencies
Depends on register layout from `arch_regs.c`, Tile kernel `PT_FLAGS_COMPAT`, and the personality order in `arch_defs_.h`.

## Risks
Wrong compatibility flag handling selects the wrong syscall table and word-size assumptions. Because the function always returns success, bad register contents are not signaled locally.

## Test Signals
Run native TileGx and compat TileGx32/TILEPro traces and verify syscall numbers resolve against the expected `syscallent.h` or `syscallent1.h` table. Tests should include headers with and without `PT_FLAGS_COMPAT`.
