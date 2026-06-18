# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dos_.h

## Purpose

`dos_.h` is a Ghostscript compatibility wrapper for MS-DOS compiler differences. It normalizes port I/O, interrupt helpers, pointer construction, and file-enumeration APIs across Microsoft C, Watcom, and Borland compilers.

## Behavior

- Always includes `<dos.h>`.
- For Watcom or Microsoft compilers:
  - Includes `<conio.h>` for `inp/outp` prototypes.
  - Maps `inport`, `outport`, `inportb`, `outportb`, `enable`, and `disable`.
  - Defines file enumeration wrappers around `_dos_findfirst` and `_dos_findnext`.
  - Splits Watcom-specific flat-model definitions from Microsoft segmented-pointer conventions.
- For other DOS compilers, assumed Borland:
  - Includes `<dir.h>`.
  - Uses `MK_FP`/`FP_OFF`.
  - Uses `findfirst`/`findnext` and `struct ffblk`.

## Dependencies / Interfaces

Exports macros and typedef-like aliases used by DOS-specific Ghostscript device code, especially old display drivers and PC framebuffer support.

## Filesystem Relevance

The file includes DOS file enumeration wrappers, but it is only a portability shim. It does not perform enumeration itself.

## Research Notes

This is legacy platform infrastructure. Modern builds outside DOS should avoid including it unless guarded by device-specific build rules.
