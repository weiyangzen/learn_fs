# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_stdenc_local.h

Read completely: 153 lines.

This header defines the standard-encoding ABI: getops function signatures, declaration/operation-table generation macros, callback typedefs, ABI version `0x00000002`, `_citrus_stdenc_ops`, `_citrus_stdenc_traits`, and `_citrus_stdenc`.

The macros `_CITRUS_STDENC_DECLS` and `_CITRUS_STDENC_DEF_OPS` are used by each encoding module to produce consistent static function prototypes and operation tables. The ABI v2 addition is `eo_get_state_desc`.

Important interactions: `citrus_stdenc_template.h` implements the macro-generated functions for most multibyte modules; `citrus_stdenc.c` validates and stores these ops.

Security/reliability notes: this is an ABI boundary. Incompatible callback signatures or wrong `lenops`/version handling can corrupt calls across dynamically loaded modules. One typedef contains a spelling typo `__reatrict`, but it is in a typedef declaration context and mirrors the source as read.
