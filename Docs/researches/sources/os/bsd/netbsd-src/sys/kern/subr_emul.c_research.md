# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_emul.c

## Summary
Implements helpers for executable emulation roots and interpreter lookup.

## Main Responsibilities
- Finds and stores the emulation root vnode for an exec package.
- Resolves dynamic interpreter paths using the emulation root when available.
- Replaces any prior saved interpreter vnode on the exec package.

## Important Behavior
`emul_find_root()` is idempotent and silently leaves `ep_emul_root` unset if the emulation has no path or the path does not exist.

`emul_find_interp()` uses `TRYEMULROOT | EMULROOTSET` when an emulation root is present, and stores the resolved interpreter vnode in `ep_interp` for later loading.

## Dependencies
Uses exec package/emulation structures, pathbuf, `namei_simple_kernel()`, `namei()`, vnode references, and compat emulation root flags.

## Risks
Missing emulation roots are not memoized, so repeated lookups can retry. The interpreter lookup deliberately uses the new program's emulation root rather than the current process root context.
