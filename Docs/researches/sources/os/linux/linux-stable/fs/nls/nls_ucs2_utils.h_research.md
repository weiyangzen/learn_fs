# File Research: sources/os/linux/linux-stable/fs/nls/nls_ucs2_utils.h

Purpose: Inline UCS-2 string utility and uppercase conversion helpers, originally derived from CIFS Unicode handling.

Core structures and definitions:
- Defines Windows private-use remappings for reserved filename characters: `UNI_ASTERISK`, `UNI_QUESTION`, `UNI_COLON`, `UNI_GRTRTHAN`, `UNI_LESSTHAN`, `UNI_PIPE`, and `UNI_SLASH`.
- Provides inline string functions: `UniStrcat`, `UniStrchr`, `UniStrcmp`, `UniStrcpy`, `UniStrlen`, `UniStrnlen`, `UniStrncat`, `UniStrncmp`, `UniStrncmp_le`, `UniStrncpy`, `UniStrncpy_le`, and `UniStrstr`.
- Provides `UniToupper()` and `UniStrupr()` unless `UNIUPR_NOUPPER` is defined.

Important behavior:
- The string helpers use `wchar_t` / `__le16` style UCS-2 code units and generally mirror C library semantics with explicit comments.
- Little-endian variants convert through `__le16_to_cpu()` / `le16_to_cpu()` / `cpu_to_le16()` where applicable.
- `UniToupper()` first uses `NlsUniUpperTable` for code points below the table size, then scans `NlsUniUpperRange[]` and applies the signed offset for matching ranges.
- `UniStrupr()` uppercases a little-endian UCS-2 string in place.

Dependencies and interfaces:
- Includes byteorder helpers, Linux types, `linux/nls.h`, `linux/unicode.h`, and `nls_ucs2_data.h`.
- Depends on exported table definitions from `nls_ucs2_utils.c`.

Design notes and risks:
- These are unsafe C-style string helpers: destination capacity is not tracked for concat/copy functions except by the explicit `n` variants.
- The functions operate on 16-bit-style code units and do not handle full Unicode scalar values or surrogate-pair semantics.
