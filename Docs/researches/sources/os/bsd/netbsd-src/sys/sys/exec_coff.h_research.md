# File Research: sources/os/bsd/netbsd-src/sys/sys/exec_coff.h

Read completely: 156 lines.

## Purpose
Defines COFF executable headers, section metadata, flag constants, alignment/layout macros, and kernel COFF preparation hooks.

## Main Interfaces
- `struct coff_filehdr`, `struct coff_aouthdr`, `struct coff_scnhdr`, `struct coff_slhdr`, `struct coff_exechdr`.
- File flags: `COFF_F_RELFLG`, `COFF_F_EXEC`, `COFF_F_LNNO`, `COFF_F_LSYMS`, byte-order/architecture flags.
- Section flags: `COFF_STYP_TEXT`, `COFF_STYP_DATA`, `COFF_STYP_BSS`, and others.
- Layout helpers: `COFF_ROUND`, `COFF_ALIGN`, `COFF_HDR_SIZE`, `COFF_BLOCK_ALIGN`, `COFF_TXTOFF`, `COFF_DATOFF`, `COFF_SEGMENT_ALIGN`.
- Kernel routines: `exec_coff_makecmds`, `exec_coff_prep_omagic`, `exec_coff_prep_nmagic`, `exec_coff_prep_zmagic`.

## Dependencies And Integration
Includes machine-dependent COFF definitions and plugs into exec image loading.

## Risks And Edge Cases
- Segment offsets depend on machine `COFF_SEGMENT_ALIGNMENT` and magic.
- Header uses C `long`/`short`, so ABI assumptions are tied to supported COFF platforms.

## Filesystem Relevance
Moderate. COFF loading reads executable file segments through VFS-backed exec paths.
