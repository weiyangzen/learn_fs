# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/zconf.h

## Purpose
Public zlib configuration header controlling symbol prefixing, compiler/platform detection, calling conventions, core typedefs, and portability defaults.

## Major Features
- `Z_PREFIX` remaps public symbols and core typedef names to `z_*` names.
- Detects DOS, OS/2, Windows, 16-bit memory models, C standard support, and selected platform quirks.
- Defines `MAX_MEM_LEVEL` and `MAX_WBITS` defaults.
- Defines prototype macro `OF(args)`.
- Defines `FAR`, `ZEXTERN`, `ZEXPORT`, and `ZEXPORTVA`.
- Defines zlib basic types: `Byte`, `uInt`, `uLong`, `Bytef`, `charf`, `intf`, `uIntf`, `uLongf`, `voidpc`, `voidpf`, `voidp`.
- Defines `z_off_t`, defaulting to `long` because the `HAVE_UNISTD_H` block is disabled with `#if 0`.
- Provides `SEEK_SET`, `SEEK_CUR`, and `SEEK_END` fallbacks.

## Platform Branches
Contains DLL import/export handling for Windows and BeOS, `ZLIB_WINAPI` support, MVS `#pragma map` aliases for short external names, and `NO_vsnprintf` settings for OS/400 and MVS.

## Plan 9 Relevance
There is no Plan 9-specific branch here. In this vendored tree, Plan 9 builds likely use the generic C path: no special DLL/export decorations, `FAR` empty, and `z_off_t long`.

## Relationship to `zconf.in.h`
This is the configured header used by the source tree. In this repository it is effectively the same as `zconf.in.h` except for the RCS identifier line.
