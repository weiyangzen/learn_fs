# File Research: sources/os/linux/linux/fs/nls/nls_utf8.c

Purpose: Linux NLS module exposing UTF-8 through the same `nls_table` interface as legacy charsets.

Core structures and data:
- `identity[256]` is initialized at module load and used as both lower and upper case tables.
- Registers charset `"utf8"`.

Important behavior:
- `uni2char()` checks output length, calls `utf32_to_utf8()`, and writes `'?'` while returning `-EINVAL` on encode failure.
- `char2uni()` calls `utf8_to_utf32()`, rejects decode failures and values above `MAX_WCHAR_T`, stores `'?'` on failure, and returns the consumed byte count on success.
- `init_nls_utf8()` initializes identity case tables and registers the module.

Dependencies and interfaces:
- Uses kernel Unicode helpers `utf32_to_utf8()` and `utf8_to_utf32()`.
- Exposes standard NLS callbacks.

Design notes and risks:
- Case conversion is explicitly byte-identity, not Unicode-aware folding.
- Error paths write fallback question marks while returning errors, so callers must honor negative return codes.
