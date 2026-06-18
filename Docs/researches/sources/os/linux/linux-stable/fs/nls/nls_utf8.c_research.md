# File Research: sources/os/linux/linux-stable/fs/nls/nls_utf8.c

Purpose: Linux NLS module exposing UTF-8 through the same `nls_table` interface as legacy charsets.

Core structures and data:
- `identity[256]` is initialized at module load and assigned as both `charset2lower` and `charset2upper`, meaning no byte-level case conversion is performed.
- The registered charset is `"utf8"`.

Important behavior:
- `uni2char()` validates output buffer length, then calls `utf32_to_utf8()`. On failure it writes `'?'` to output and returns `-EINVAL`.
- `char2uni()` calls `utf8_to_utf32()`, rejects decode failures or code points above `MAX_WCHAR_T`, stores `'?'` in `*uni` on failure, and returns the consumed byte count on success.
- `init_nls_utf8()` initializes identity case tables and registers the module.

Dependencies and interfaces:
- Uses kernel Unicode helpers `utf32_to_utf8()` and `utf8_to_utf32()`.
- Exposes standard `struct nls_table` callbacks.

Design notes and risks:
- Case conversion is explicitly a no-op; consumers needing Unicode-aware case folding need separate logic.
- Error paths write fallback question mark values while returning an error, so callers should not ignore negative return codes.
