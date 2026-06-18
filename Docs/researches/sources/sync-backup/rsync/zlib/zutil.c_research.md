# sources/sync-backup/rsync/zlib/zutil.c

Purpose: target-dependent utility implementation for zlib. It supplies version/error helpers, compile-flag introspection, optional fallback memory functions, optional debug failure handling, and default allocation/free routines used by deflate/inflate internals when callers do not provide custom allocators.

Important APIs/types/functions: `z_errmsg` maps zlib status codes to static strings via `ERR_MSG`. `zlibVersion` returns `ZLIB_VERSION`. `zlibCompileFlags` encodes sizes of `uInt`, `uLong`, pointer, and `z_off_t`, plus compile-time features such as `DEBUG`, assembly, `ZLIB_WINAPI`, `BUILDFIXED`, `DYNAMIC_CRC_TABLE`, gzip/compress disables, PKZIP workaround, fastest mode, and printf safety variants. `zError` exposes error-string lookup. Fallback `zmemcpy`, `zmemcmp`, and `zmemzero` are built when `HAVE_MEMCPY` is absent. `zcalloc` and `zcfree` cover generic and historical 16-bit allocation paths.

Control flow: normal builds take the generic allocator path: `zcalloc` ignores `opaque`, allocates with `malloc` on wider-than-16-bit `uInt` targets or `calloc` otherwise, and `zcfree` calls `free`. Legacy Turbo C and Microsoft C paths normalize or use far allocations for 64 KiB segmented-memory constraints.

State and persistence behavior: no durable state. The only process state is the exported static error-message table, optional debug verbosity, and the Turbo C pointer table used to recover original far pointers. Allocation state belongs to the C heap or legacy heap APIs.

Dependencies/integration: includes `zutil.h` and, unless `Z_SOLO`, `gzguts.h`. It is used by zlib implementation files through `ZALLOC`, `ZFREE`, `TRY_FREE`, error-message macros, and optional memory wrappers.

Risks/test signals: integer overflow on `items * size` is inherited from the old zlib allocator contract. Legacy segmented-memory code is fragile and not thread-protected. Test signals are successful deflate/inflate initialization under default allocators, `zlibCompileFlags` matching build options, and fallback memory routines behaving like libc equivalents.
