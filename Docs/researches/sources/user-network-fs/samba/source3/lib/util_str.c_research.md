# sources/user-network-fs/samba/source3/lib/util_str.c

## Purpose
`util_str.c` provides source3 string helpers for case-insensitive comparison, bounded buffer traversal, multibyte-aware character counting and case conversion, list membership, name validation, shell escaping, size parsing, and efficient path assembly.

## Important APIs and Functions
Exports include `strnequal`, `skip_string`, `str_charnum`, `trim_char`, `in_list`, `string_truncate`, `strlower_m`, `strupper_m`, `fstr_sprintf`, `conv_str_size`, `talloc_asprintf_strupper_m`, `talloc_asprintf_strlower_m`, `validate_net_name`, `escape_shell_string`, and `full_path_tos`. Internal helpers `unix_strlower` and `unix_strupper` convert through UTF-16LE for multibyte-aware casing. `toupper_ascii_fast_table` provides a fast ASCII upper-case path.

## Control Flow and Behavior
Most functions optimize for common ASCII cases and fall back to Samba charset conversion when high-bit bytes are encountered. `trim_char` handles front and back trimming in place and falls back to `trim_string` when a potential multibyte boundary is encountered near the trim point. `in_list` tokenizes a configured list with `next_token_talloc`. `escape_shell_string` walks codepoints, preserving multibyte characters and tracking unquoted, single-quoted, double-quoted, and backslash-escaped states to add shell escapes only where needed. `full_path_tos` writes into a caller stack buffer when large enough and allocates from `talloc_tos()` only when necessary.

## State and Persistence
The file has no durable state. It uses stackframes and talloc ownership for temporary conversions and returned strings. `escape_shell_string` returns `SMB_MALLOC` memory requiring `SAFE_FREE` by callers, while the `talloc_asprintf_*` functions return talloc-owned buffers.

## Dependencies and Integration Points
It depends on Samba charset conversion (`push_ucs2_talloc`, `convert_string`, `strlower_w`, `strupper_w`, `next_codepoint`), loadparm utilities, token parsing, `smb_strtox` size parsing, and fixed-size Samba string types such as `fstring`. These helpers are widely integrated across path handling, configuration parsing, name validation, command invocation, and protocol string processing.

## Risks and Edge Cases
`string_truncate` is byte-count based and can cut multibyte strings. `strlower_m` and `strupper_m` assume case conversion does not expand the remaining buffer and forcibly terminates on conversion errors. `validate_net_name` only checks invalid characters within `max_len`; it does not reject names longer than `max_len` by itself. `escape_shell_string` is careful but shell escaping is inherently context sensitive, and callers must know it targets UNIX charset shell arguments. `full_path_tos` always inserts `'/'`, so callers must avoid double separators if that matters.

## Test Signals
Tests should cover ASCII and multibyte case conversion, conversion error termination, `skip_string` with unterminated buffers and pointer overflow, trimming complete strings and multibyte suffixes, list parsing with case sensitivity, shell metacharacters inside and outside quotes, invalid UTF-8 handling, and `full_path_tos` stack-buffer vs talloc allocation paths.
