# sources/test-tools/strace/src/linux/tile/arch_defs_.h

## Purpose
Defines Tile architecture personality metadata used by the generic `arch_defs.h` layer. Tile supports two personalities: native TILE-Gx and either TILEPro or TILE-Gx32 compat, depending on the build target.

## Important APIs, Types, and Functions
Defines `SUPPORTED_PERSONALITIES 2`, `PERSONALITY0_AUDIT_ARCH` as `AUDIT_ARCH_TILEGX`, and `PERSONALITY1_AUDIT_ARCH` as `AUDIT_ARCH_TILEPRO` on `__tilepro__` builds or `AUDIT_ARCH_TILEGX32` otherwise. It also sets `CAN_ARCH_BE_COMPAT_ON_64BIT_KERNEL 1` and defaults to personality 1 on TILEPro builds.

## Control Flow and Integration
All behavior is preprocessor-driven. `syscall_name.c`, `filter_seccomp.c`, `basic_filters.c`, and `syscall.c` consume these definitions to size personality arrays, label audit arches, and decide compat behavior.

## State and Persistence
No runtime state. The persistent result is compile-time personality configuration baked into strace.

## Dependencies
Depends on Linux audit architecture constants and on `arch_defs.h` defaults for names, word sizes, and personality designators not overridden here.

## Risks
Misconfigured audit arches break seccomp filter generation and syscall-info personality detection. The `__tilepro__` conditional is sensitive because it changes both compat audit arch and default personality.

## Test Signals
Build TileGx and TilePro variants, inspect `strace -V` personality reporting where available, and verify syscall filtering by audit arch for native and compat Tile processes.
