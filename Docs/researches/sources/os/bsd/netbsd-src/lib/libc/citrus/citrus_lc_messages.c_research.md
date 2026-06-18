# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_lc_messages.c

Locale loader for `LC_MESSAGES`.

Key behavior:
- Defines the category prefix and uses the generic Citrus locale template.
- `_citrus_LC_MESSAGES_uninit` frees yes/no expressions and strings.
- Normal DB initialization reads `yesexpr`, `noexpr`, `yesstr`, and `nostr` string values from a Citrus DB.
- Fallback initialization reads the same values line-by-line from a plain memory stream.
- Category DB path is `LC_MESSAGES/SYS_LC_MESSAGES`; magic is `CtrsME10`.

Error handling:
- Any missing/malformed field releases already allocated strings and returns `EFTYPE`.
