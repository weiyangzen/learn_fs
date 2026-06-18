# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_iso2022.c

Read completely: 1349 lines.

This module implements ISO-2022 ctype and stdenc support. It is a configurable, state-dependent escape-sequence engine with G0-G3 designation, GL/GR invocation, single-shift handling, optional 8-bit behavior, and recommended charset placement.

Key structures: `_ISO2022Charset` records charset type/final/intermediate/version; `_ISO2022State` stores current G sets, GL/GR/single-shift selectors, a partial escape buffer, and initialization flags; `_ISO2022EncodingInfo` stores recommendation arrays, initial G sets, max charset policy, and flags.

Key behavior: `_citrus_ISO2022_parse_variable` parses tokens such as charset recommendations, `INITn=...`, `MAXn`, and flags (`8BIT`, `LS*`, `SS*`, `NOOLD`). `_ISO2022_sgetwchar` consumes shifts and escape sequences, updates designation state, and extracts wide-character encodings. `_citrus_ISO2022_mbrtowc_priv` manages restartable partial escape buffers. `_ISO2022_sputwchar` chooses a charset plane, emits designation/invocation sequences, and writes encoded bytes. `put_state_reset` emits a reset sequence by outputting NUL and dropping the final data byte.

Important interactions: exports through ctype/stdenc templates and is consumed by `iconv_std`. It uses only variable strings, no external mapping file in this source.

Security/reliability notes: the escape buffer is fixed at 7 bytes and the parser rejects too-long/incomplete sequences through restart or `EILSEQ`. Variable parsing allocates recommendation arrays and frees them only on parse failure; module uninit is empty, so successful initialization retains those arrays for module lifetime but does not release them on close. Comments note that output conversion mutates state before all buffer-size failures are known; callers such as `iconv_std` save/restore state around failures to compensate.
