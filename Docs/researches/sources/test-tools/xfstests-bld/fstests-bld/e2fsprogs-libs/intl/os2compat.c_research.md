# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/os2compat.c

Purpose: supplies OS/2 EMX runtime compatibility for libintl directory and environment handling.

Important APIs and control flow: `_nl_getenv(name)` calls `DosScanEnv` so DLL builds can read environment variables reliably. The constructor `nlos2_initialize()` reads `UNIXROOT` and `GNULOCALEDIR`, then initializes `_nlos2_libdir`, `_nlos2_localealiaspath`, and `_nlos2_localedir` to either `GNULOCALEDIR`, `UNIXROOT`-prefixed configure paths, or hardwired defaults. If the computed locale directory fits in `MAXPATHLEN`, it copies it to `libintl_nl_default_dirname`.

State and persistence: global path pointers and a fixed-size default dirname buffer persist for process lifetime. Allocated prefixed paths are intentionally not freed.

Dependencies and integration: included by `osdep.c` on `__EMX__`; paired with `os2compat.h`, which rewrites `LIBDIR`, `LOCALEDIR`, `LOCALE_ALIAS_PATH`, `getenv`, and case-insensitive string APIs.

Risks and test signals: constructor allocation failures are not checked before later `strlen`, and path concatenation assumes configured paths begin suitably. Test with and without `UNIXROOT`/`GNULOCALEDIR`, long paths, and DLL environment visibility.
