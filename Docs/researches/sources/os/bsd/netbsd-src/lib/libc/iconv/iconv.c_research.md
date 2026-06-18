# File Research: sources/os/bsd/netbsd-src/lib/libc/iconv/iconv.c

Public libc `iconv` wrapper around Citrus conversion internals.

APIs:
- `iconv_open(out, in)`
- `iconv_close(handle)`
- `iconv(handle, in, szin, out, szout)`
- NetBSD extensions `__iconv`, `__iconv_get_list`, `__iconv_free_list`

Behavior:
- `iconv_open` calls `_citrus_iconv_open(&handle, _PATH_ICONV, in, out)` and maps missing conversion data to `EINVAL`.
- `iconv_close` rejects null or `(iconv_t)-1` handles with `EBADF`.
- `iconv` and `__iconv` call `_citrus_iconv_convert`; `__iconv` accepts flags and optionally reports invalid count.
- List helpers delegate to Citrus ESDB list routines.

Dependencies: Citrus modules, `namespace.h`, weak aliases for public names.
