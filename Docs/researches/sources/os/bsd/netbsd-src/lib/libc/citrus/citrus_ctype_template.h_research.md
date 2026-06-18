# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_ctype_template.h

Reusable template implementation for encoding-specific ctype modules.

Key behavior:
- Requires caller-defined macros for function naming, encoding info/state types, state packing/unpacking, state dependency, and encoding-specific private conversion routines.
- Implements common `mbtowc`, `mbrtowc`, `mbsrtowcs`, `mbsnrtowcs`, `mbstowcs`, `wcrtomb`, `wcsrtombs`, `wcsnrtombs`, `wcstombs`, `wctomb`, `btowc`, and `wctob` behavior.
- Handles restartable state through `_RESTART_BEGIN`/`_RESTART_END`, using either caller-provided private state or method-specific internal state.
- Supports state-dependent encodings with reset-sequence emission before null conversions.
- Provides `ctype_getops`, `ctype_init`, and `ctype_uninit` template implementations.
- Verifies `_ENCODING_STATE` alignment is compatible with locale multibyte state storage.

Notable details:
- Conversion loops preserve source pointers until success rules require publishing them.
- Stateful output conversion restores state if an output buffer cannot fit the next multibyte sequence.
- Some legacy comments note limitations, such as `ctype_mbsinit` checking `state.chlen == 0`.
