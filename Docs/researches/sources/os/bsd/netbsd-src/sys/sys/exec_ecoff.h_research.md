# File Research: sources/os/bsd/netbsd-src/sys/sys/exec_ecoff.h

Read completely: 187 lines.

## Purpose
Defines ECOFF executable formats, including optional padded 32-bit layouts, segment offset/alignment macros, and ECOFF kernel exec hooks.

## Main Interfaces
- Optional `ECOFF32_PAD` block defining fixed-width `ecoff32_*` types and `ecoff32_*` headers.
- Native `struct ecoff_filehdr`, `struct ecoff_aouthdr`, `struct ecoff_scnhdr`, `struct ecoff_exechdr`.
- Magic values: `ECOFF_OMAGIC`, `ECOFF_NMAGIC`, `ECOFF_ZMAGIC`.
- Layout helpers: `ECOFF_ROUND`, `ECOFF_BLOCK_ALIGN`, `ECOFF_TXTOFF`, `ECOFF_DATOFF`, `ECOFF_SEGMENT_ALIGN`, plus 32-bit variants.
- Kernel routines: `exec_ecoff_makecmds`, `cpu_exec_ecoff_probe`, `cpu_exec_ecoff_setregs`, `exec_ecoff_prep_*`.

## Dependencies And Integration
Includes endian and machine ECOFF definitions. Used by architecture compatibility exec paths.

## Risks And Edge Cases
- Optional 32-bit padded layout exists only when `ECOFF32_PAD` is defined.
- Layout depends on machine-dependent padding and segment alignment macros.
- ECOFF probing and register setup are CPU-dependent.

## Filesystem Relevance
Moderate. Another exec format consuming file contents through VFS/vnode exec reads.
