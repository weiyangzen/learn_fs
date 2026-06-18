# File Research: sources/os/bsd/netbsd-src/lib/libterminfo/compile.c

Runtime/compiler support for converting textual terminfo entries into NetBSD’s compact binary `TIC` representation.

Key responsibilities:
- Parses terminfo capability strings into booleans, numerics, strings, aliases, descriptions, and user-defined extras.
- Encodes values into typed growable buffers (`TBUF`) using little-endian fixed-size fields.
- Supports old/new terminfo record formats:
  - Type 1 uses 16-bit numeric values.
  - Type 3 uses 32-bit numeric values.
- Under `TERMINFO_COMPAT`, promotes old type-1 records to type-3 when values exceed `INT16_MAX`.
- Provides lookup helpers for already-stored capabilities and extras to avoid duplicates.
- Converts escaped strings:
  - caret escapes,
  - octal escapes,
  - common backslash escapes,
  - newline folding in capability strings.
- Flattens a compiled `TIC` object into the serialized database/runtime format.
- Frees all dynamically allocated compiled-entry storage.

Important functions:
- `_ti_compile`
- `_ti_flatten`
- `_ti_freetic`
- `_ti_grow_tbuf`
- `_ti_find_cap`
- `_ti_find_extra`
- `_ti_store_extra`
- `_ti_get_token`
- `_ti_getname`
- `_ti_encode_buf_id_num`
- `_ti_encode_buf_id_count_str`
- `_ti_encode_buf_id_flags`

Research notes:
- This file is only built when full terminfo compilation support is enabled.
- It is used by `term.c` when `TERMINFO` or `TERMCAP` contains inline terminal descriptions rather than paths.
- Unknown capabilities are stored only when `TIC_EXTRA` is enabled; otherwise they are ignored with optional warnings.
