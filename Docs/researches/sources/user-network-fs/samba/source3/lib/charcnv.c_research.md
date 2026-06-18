# sources/user-network-fs/samba/source3/lib/charcnv.c

Purpose: provides SMB character set conversion helpers between Samba Unix strings, DOS codepage strings, and UTF-16LE/UCS2 wire strings.

Important APIs/types/functions: `gfree_charcnv()`, `push_ascii()`, `pull_ascii()`, internal talloc pull helpers for ASCII and UCS2, `push_ucs2()`, `push_string_check_fn()`, `push_string_base()`, `pull_string_talloc()`, and `rpcstr_push_talloc()`.

Control flow: push functions choose ASCII or UTF-16LE based on flags and SMB `FLAGS2_UNICODE_STRINGS`, optionally uppercase, align UCS2 buffers unless `STR_NOALIGN`, and use `convert_string()` or `convert_string_talloc()`. Pull functions bound client-provided terminated lengths with `strnlen/strnlen_w`, reject `-1` lengths in newer paths, append NUL when conversion did not include it, and panic on invalid API use.

State and persistence: no durable state; `gfree_charcnv()` releases global iconv handles. Talloc pull variants allocate destination strings for callers.

Dependencies/integration: iconv conversion layer, Samba charset helpers, SMB flags, Unicode case conversion, talloc, and panic/debug infrastructure.

Risks/test signals: invalid lengths intentionally panic, and failed conversion may clear destination output. Tests should cover ASCII/Unicode selection, alignment, termination with bounded source lengths, uppercase conversion, conversion failure, empty strings, large client lengths near the 1 MiB guard, and RPC string allocation.
