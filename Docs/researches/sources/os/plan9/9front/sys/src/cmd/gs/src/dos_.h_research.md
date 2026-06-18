# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dos_.h

This is a Ghostscript portability header for MS-DOS compiler differences. It normalizes low-level DOS I/O, interrupt, pointer, and file-enumeration interfaces across Microsoft C, Watcom C, and Borland C.

Key responsibilities:
- Includes `<dos.h>` and, for Microsoft/Watcom, `<conio.h>` because port I/O prototypes are there for those compilers.
- Maps port I/O APIs to common names: `inport`, `inportb`, `outport`, and `outportb`.
- Maps interrupt enable/disable calls to `_enable()` and `_disable()` on Microsoft/Watcom.
- Defines segment/pointer helpers `MK_PTR` and `PTR_OFF`, with different behavior for Watcom flat model, Microsoft, and Borland segmented model.
- Normalizes register-union field selection through `rshort`.
- Normalizes DOS file enumeration structures and functions:
  - Microsoft/Watcom use `_dos_findfirst`, `_dos_findnext`, `struct find_t` or `struct _find_t`, and `ff_name name`.
  - Borland uses `<dir.h>`, `findfirst`, `findnext`, and `struct ffblk`.

Important dependencies:
- Declared in `lib.mak` as `dos__h=$(GLSRC)dos_.h`.
- Used by DOS/platform files such as `gp_iwatc.c`, `gp_dosfs.c`, `gp_dosfe.c`, `gp_msdos.c`, `zdosio.c`, and hardware/display-related code such as `gdevherc.c` and `gdevpcfb.h`.

Notable implementation details:
- The file deliberately abstracts several incompatible DOS compiler memory models.
- It includes direct I/O port support, which is relevant to old display/printer hardware paths.
- It defines `O_BINARY`, `fdopen`, `stdprn`, and related aliases for Microsoft C compatibility.

Filesystem relevance:
- The file touches file enumeration abstractions for DOS builds, but it does not perform enumeration itself.
- It is a portability layer used by Ghostscript's DOS filesystem/platform code.
- No Plan 9 filesystem, VFS, or storage logic is present.

Research classification: historical MS-DOS compiler compatibility shim for Ghostscript platform and device code.
