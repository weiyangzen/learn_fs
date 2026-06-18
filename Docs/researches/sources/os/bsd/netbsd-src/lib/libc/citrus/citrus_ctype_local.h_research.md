# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_ctype_local.h

Internal ABI definition for Citrus ctype modules.

Key behavior:
- Defines getops naming macros, module declaration macros, and ops-table construction macro.
- Declares all function pointer typedefs for ctype operations.
- Defines `_CITRUS_CTYPE_ABI_VERSION` as `0x00000003`.
- Documents ABI evolution: v2 added `btowc`/`wctob`; v3 added `mbsnrtowcs`/`wcsnrtombs`.
- Defines `_citrus_ctype_ops_rec` and `_citrus_ctype_rec`.
- Sets default ctype name/header/ops to `NONE` / `citrus_none.h`.

Purpose:
- This is the contract every Citrus ctype module must implement or be adapted to by fallbacks.
