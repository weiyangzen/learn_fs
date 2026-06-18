# File Research: sources/os/bsd/netbsd-src/sys/sys/exec_aout.h

Read completely: 184 lines.

## Purpose
Defines the legacy a.out executable header, magic values, machine-id/flag encoding, segment address/offset macros, and kernel preparation routines.

## Main Interfaces
- `struct exec`: a.out header fields for text, data, bss, symbols, entry, relocation sizes.
- Magic values: `OMAGIC`, `NMAGIC`, `ZMAGIC`, `QMAGIC`.
- Flags: `EX_DYNAMIC`, `EX_PIC`, `EX_DPMASK`.
- Header field macros: `N_GETMAGIC`, `N_GETMAGIC2`, `N_GETMID`, `N_GETFLAG`, `N_SETMAGIC`.
- Layout macros: `N_ALIGN`, `N_BADMAG`, `N_TXTADDR`, `N_DATADDR`, `N_BSSADDR`, `N_TXTOFF`, `N_DATOFF`, relocation and symbol/string offsets.
- Kernel handlers: `exec_aout_makecmds`, `exec_aout_prep_*`, `cpu_exec_aout_makecmds`.

## Dependencies And Integration
Uses endian conversion, a.out machine IDs, and machine-dependent a.out definitions. Plugs into the generic exec switch.

## Risks And Edge Cases
- `a_midmag` is network-byte-order encoded for newer format variants.
- Layout macros depend on `AOUT_LDPGSZ` and magic-specific historical behavior.
- `QMAGIC` is marked deprecated but still recognized.

## Filesystem Relevance
Moderate. It is an exec format consuming vnode file contents through the exec framework.
