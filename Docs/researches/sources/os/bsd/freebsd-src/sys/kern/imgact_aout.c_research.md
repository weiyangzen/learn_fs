# File Research: sources/os/bsd/freebsd-src/sys/kern/imgact_aout.c

## Summary
Implements the legacy FreeBSD a.out image activator for i386 or amd64 running 32-bit a.out binaries.

## Main Responsibilities
- Defines the a.out `sysentvec` for i386 or amd64 compatibility.
- Provides stack fixup that writes `argc` below the stack base.
- Validates a.out headers, machine IDs, magic variants, sizes, entry address, and resource limits.
- Creates a new VM space, maps text/data/bss, maps the stack, sets process ABI state, and registers an execsw entry.

## Key APIs
- `exec_aout_imgact()` is the image activator.
- `aout_fixup()` writes the initial `argc` word.
- `aout_sysent()` initializes the amd64 32-bit signal-code size from embedded VDSO symbols.
- `EXEC_SET(aout, aout_execsw)` registers the activator.

## Important Behavior
The loader recognizes FreeBSD, BSDI, and NetBSD-compatible a.out markings. It handles `ZMAGIC` and `QMAGIC`, including network-byte-order compatibility. For BSD/OS-style `MID_ZERO` QMAGIC binaries, it passes `PS_STRINGS`.

The loader rejects invalid entry points, non-page-rounded text/data sizes, truncated files, and text/data/bss sizes above process/system limits. It unlocks the executable vnode around `exec_new_vmspace()` to avoid deadlocks, then maps text executable/readable and data writable with copy-on-write.

## Risks
This is compatibility code for old executable formats. It has architecture-specific assumptions, 32-bit address bounds on amd64, and manual VM layout logic. Mistakes could map malformed binaries or create unsafe legacy ABI process state.
