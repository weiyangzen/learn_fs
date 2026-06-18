# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_euc.c

Read completely: 437 lines.

This module implements configurable EUC ctype and stdenc support. Encoding variables supply four byte counts, four bit masks, and a global mask that determine character-set selection and wide-character construction.

Key behavior: `_citrus_EUC_parse_variable` reads counts and bit values from the module variable string, requiring each count to be 1 through 4. `_citrus_EUC_cs` classifies the first byte into G0/G1/SS2/SS3. `mbrtowc_priv` buffers up to three bytes and constructs a wide value by applying masks/bits. `wcrtomb_priv` finds the matching charset bits, emits SS2/SS3 prefixes when needed, and writes the configured number of bytes.

Important interactions: this module relies entirely on ESDB-provided variables for correctness; it exports through ctype/stdenc templates.

Security/reliability notes: variable parsing rejects missing or malformed fields with `EFTYPE`. The tableless conversion path bounds output length with `n < i` checks. Callers must ensure the variable string is NUL-terminated or otherwise safe for the parser’s `while (*v)` style scanning.
