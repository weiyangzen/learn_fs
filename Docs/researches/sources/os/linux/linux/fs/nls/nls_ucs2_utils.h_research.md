# File Research: sources/os/linux/linux/fs/nls/nls_ucs2_utils.h

Purpose: Inline UCS-2 string utility and uppercase conversion helpers, derived from CIFS/server Unicode handling.

Core structures and definitions:
- Defines Windows private-use remappings for reserved filename characters: `UNI_ASTERISK`, `UNI_QUESTION`, `UNI_COLON`, `UNI_GRTRTHAN`, `UNI_LESSTHAN`, `UNI_PIPE`, and `UNI_SLASH`.
- Provides inline string helpers: `UniStrcat`, `UniStrchr`, `UniStrcmp`, `UniStrcpy`, `UniStrlen`, `UniStrnlen`, `UniStrncat`, `UniStrncmp`, `UniStrncmp_le`, `UniStrncpy`, `UniStrncpy_le`, and `UniStrstr`.
- Provides `UniToupper()` and `UniStrupr()` unless `UNIUPR_NOUPPER` is defined.

Important behavior:
- String helpers mirror C library style APIs over `wchar_t` / `__le16`-style UCS-2 code units.
- Little-endian variants convert via kernel byteorder helpers.
- `UniToupper()` first indexes `NlsUniUpperTable`, then scans `NlsUniUpperRange[]`.
- `UniStrupr()` uppercases a little-endian UCS-2 string in place.

Dependencies and interfaces:
- Includes byteorder helpers, Linux types, `linux/nls.h`, `linux/unicode.h`, and `nls_ucs2_data.h`.
- Depends on table definitions exported by `nls_ucs2_utils.c`.

Design notes and risks:
- Several helpers are unsafe C-style copy/concat functions with no destination capacity tracking.
- Operates on 16-bit code units and does not handle full Unicode scalar or surrogate-pair semantics.
