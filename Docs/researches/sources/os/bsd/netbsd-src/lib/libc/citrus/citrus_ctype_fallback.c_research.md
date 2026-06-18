# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_ctype_fallback.c

Compatibility implementations for newer ctype ABI operations when older modules lack them.

Key behavior:
- `btowc` fallback converts one byte through `mbrtowc` with a fresh private state.
- `wctob` fallback converts a wide char through `wcrtomb` and succeeds only if exactly one byte is produced.
- `mbsnrtowcs` fallback loops over a bounded byte input using `mbrtowc`.
- `wcsnrtombs` fallback loops over bounded wide input using `wcrtomb`, preserving state if the output buffer is too small.

Notable details:
- Uses stack storage sized as `mbstate_t` for private state.
- Returns standard restartable conversion result counts and `(size_t)-1` on conversion error.
