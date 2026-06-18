# sources/sync-backup/rsync/zlib/zconf.h

Purpose: central portability and ABI configuration header for zlib. It defines optional symbol prefixing, platform detection, calling conventions, type aliases, large-file support, function prototype compatibility, memory/window limits, and exported/internal symbol macros.

Important APIs/types/functions: the `Z_PREFIX` block renames all public and internal linked symbols and typedefs. Platform sections define `MSDOS`, `OS2`, `WINDOWS`, `WIN32`, `SYS16BIT`, `MAXSEG_64K`, `UNALIGNED_OK`, `STDC`, and `STDC99`. Core configuration includes `MAX_MEM_LEVEL`, `MAX_WBITS`, `OF`, `Z_ARG`, `FAR`, `ZEXTERN`, `ZEXPORT`, `ZEXPORTVA`, `Byte`, `uInt`, `uLong`, `Bytef`, `charf`, `intf`, `uIntf`, `uLongf`, `voidp` variants, `z_crc_t`, `z_off_t`, and `z_off64_t`.

Control flow: no runtime code, but extensive preprocessor control flow selects ABI and type definitions per compiler/platform. Large-file logic maps `_LARGEFILE64_SOURCE`, `_LFS64_LARGEFILE`, and `_FILE_OFFSET_BITS=64` to zlib's 64-bit offset types. MVS pragmas map long external names to linker-safe short names.

State and persistence: no mutable state. It defines compile-time configuration that persists into every object file including `zlib.h`; inconsistent compile flags across objects can create ABI mismatches.

Dependencies and integration points: included by `zlib.h` and therefore almost every zlib source. It conditionally includes system headers such as `limits.h`, `sys/types.h`, `stdarg.h`, `stddef.h`, and `unistd.h`. `deflate.c`, `inflate.c`, gz modules, and utility code all depend on its typedefs and macros.

Risks: changes can break binary compatibility, symbol names, DLL import/export behavior, large-file offsets, or 16-bit/FAR pointer support. Reducing `MAX_WBITS` or `MAX_MEM_LEVEL` affects compression compatibility and memory use. `Z_PREFIX` must be applied consistently across all zlib users to avoid link failures.

Test signals: build matrix across POSIX, Windows, large-file enabled/disabled, `Z_PREFIX`, `ZLIB_DLL`, `ZLIB_WINAPI`, `Z_SOLO`, and reduced memory/window settings. ABI checks should verify exported names and type sizes. Runtime tests should include gz seek/tell offsets and normal deflate/inflate after configuration changes.
