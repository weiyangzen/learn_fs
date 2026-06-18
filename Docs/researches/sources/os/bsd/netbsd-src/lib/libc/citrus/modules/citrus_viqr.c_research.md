# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_viqr.c

## Scope

Implements the Citrus ctype/stdenc module for VIQR Vietnamese mnemonic encoding.

## APIs And Behavior

- Builds a mnemonic tree from RFC 1456 mappings and extension mappings at module initialization.
- `_citrus_VIQR_mbrtowc_priv()` walks mnemonic trie state, handles escape characters, and returns the longest valid mnemonic mapping.
- `_citrus_VIQR_wcrtomb_priv()` emits mnemonic strings for mapped characters and uses escape disambiguation for ambiguous literal bytes.
- `_citrus_VIQR_put_state_reset()` clears pending mnemonic/disambiguation state.
- Stdenc maps characters through csid `0`.

## Dependencies

Uses `TAILQ` for mnemonic child lists, dynamic allocation for mnemonic trie nodes, Citrus ctype/stdenc templates, and standard string/wide-character APIs.

## Risks And Invariants

- The mnemonic trie must be destroyed on module uninit to avoid leaks.
- Longest-prefix matching and escape disambiguation are central to reversible VIQR conversion.
- `mb_cur_max` is derived from the longest configured mnemonic and must stay within `MB_LEN_MAX`.
