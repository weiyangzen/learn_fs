# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lfunc.c

## Role

`lfunc.c` manages Lua closures, prototypes, and upvalues.

## Main Responsibilities

- Allocates C closures, Lua closures, fresh upvalues, and function prototypes.
- Finds or creates open upvalues for stack slots, keeping open upvalues sorted by stack level.
- Resurrects dead open upvalues when reused.
- Closes open upvalues at or above a stack level by copying stack values into the upvalue object and moving it to the regular GC list.
- Frees upvalues and prototypes, including all prototype arrays.
- Looks up active local-variable names for debug information.

## Integration Points

The parser creates prototypes, the VM creates/finds upvalues for closures, `ldo.c` closes upvalues during error recovery, and `lgc.c` frees/traverses these objects.

## Risk Notes

Open upvalue list ordering and GC color transitions are critical. Closing an upvalue must preserve the captured value and update collector invariants.
