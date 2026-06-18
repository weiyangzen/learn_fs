# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_stdenc.h

Read completely: 148 lines.

This is the standard-encoding public/internal API header. It defines generic state-description IDs and states, includes `citrus_stdenc_local.h` for structures and callback types, declares open/close/default symbols, and provides inline wrappers for all core operations.

Key wrappers: `_citrus_stdenc_init_state`, `_citrus_stdenc_mbtocs`, `_citrus_stdenc_cstomb`, `_citrus_stdenc_mbtowc`, `_citrus_stdenc_wctomb`, `_citrus_stdenc_put_state_reset`, state-size and max-byte accessors, and `_citrus_stdenc_get_state_desc`.

Important interactions: encoding modules implement the callback table expected here; iconv modules consume these wrappers. The namespace header aliases shorter `_stdenc_*` names onto these functions.

Security/reliability notes: wrappers rely on `_DIAGASSERT` for null callback validation and then dispatch directly. Release builds depend on prior validation in `_citrus_stdenc_open`.
