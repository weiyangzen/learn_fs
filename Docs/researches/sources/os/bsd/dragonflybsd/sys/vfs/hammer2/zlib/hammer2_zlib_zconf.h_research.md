# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_zconf.h

Source read: complete file, 292 lines.

Purpose: zlib configuration header for HAMMER2’s embedded copy, with DragonFly-specific symbol prefixing enabled so the files can be included in kernel configuration without colliding with other zlib symbols.

Key definitions:
- Defines `Z_PREFIX`, then maps public and internal zlib symbols such as `inflate`, `deflate`, `adler32`, `_tr_*`, `inflate_table`, and typedef names to `z_*` names.
- Detects C standard support and defines `STDC`/`STDC99`.
- Defines zlib public ABI types: `Byte`, `uInt`, `uLong`, `Bytef`, `charf`, `voidp`, `voidpf`, and related aliases.
- Sets `MAX_MEM_LEVEL`, `MAX_WBITS`, `Z_HAVE_UNISTD_H`, `Z_HAVE_STDARG_H`, and `z_off_t`/`z_off64_t` behavior.
- Includes DragonFly/kernel-flavored headers such as `<sys/limits.h>` and `<sys/stdarg.h>`.

Integration:
- Included through `hammer2_zlib.h` and all internal zlib source files.
- Its prefix mapping controls linker-visible names for the entire embedded zlib copy.

Risks and review notes:
- The forced `Z_PREFIX` is intentional for kernel coexistence; removing it can cause duplicate symbol conflicts.
- Type-size and large-file branches are inherited from portable zlib, but this kernel copy only needs a constrained subset; unused portability paths should still compile cleanly under DragonFly headers.
