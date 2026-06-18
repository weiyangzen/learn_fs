# sources/sync-backup/rsync/zlib/zutil.h

Purpose: internal zlib configuration and utility header. Applications are warned not to include it directly; it defines implementation-only aliases, constants, platform hooks, diagnostics, allocation macros, byte-swap helpers, and memory-function selection used across the bundled zlib sources.

Important APIs/types/functions: it sets `ZLIB_INTERNAL`, includes rsync's `../rsync.h` before `zlib.h`, defines `local`, `uch/ush/ulg` aliases, declares `z_errmsg`, and provides `ERR_MSG` plus `ERR_RETURN`. Compression constants include `DEF_WBITS`, `DEF_MEM_LEVEL`, block types, `MIN_MATCH`, `MAX_MATCH`, and `PRESET_DICT`. It selects `OS_CODE`, `F_OPEN`, `fdopen` compatibility, `zmemcpy`/`zmemcmp`/`zmemzero`, debug `Assert`/`Trace*` macros, `zcalloc`, `zcfree`, `ZALLOC`, `ZFREE`, `TRY_FREE`, and `ZSWAP32`.

Control flow: preprocessing determines platform behavior from macros such as `MSDOS`, `WIN32`, `VMS`, `MACOS`, `_WIN32_WCE`, `Z_SOLO`, `HAVE_MEMCPY`, and compiler identifiers. Runtime code includes this header to normalize target differences before using utility macros.

State and persistence behavior: no durable state. It governs how zlib code touches stream allocator state, emits debug traces, and opens files. `ZALLOC` and `ZFREE` route all internal heap state through the `z_stream` allocator hooks.

Dependencies/integration: integrates the zlib internals with rsync by including `../rsync.h`, which can affect platform definitions and libc availability. It also bridges to `zlib.h` public types and optionally C library headers through rsync configuration.

Risks/test signals: platform macro mistakes can silently change gzip OS metadata, file opening modes, memory function semantics, or allocation paths. Important tests are cross-platform zlib builds, compression/decompression round trips, gzip file I/O, and builds with/without `HAVE_MEMCPY`, `DEBUG`, `Z_SOLO`, and large-file support.
