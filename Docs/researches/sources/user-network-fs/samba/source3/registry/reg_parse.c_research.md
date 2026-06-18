# sources/user-network-fs/samba/source3/registry/reg_parse.c

## Purpose
`reg_parse.c` parses Windows `.reg` files line-by-line or from a file descriptor and emits structured events through `struct reg_parse_callback`. It handles keys, key deletes, values, value deletes, comments, line continuations, and file/string charset conversion.

## Important APIs, Types, And Functions
The opaque `struct reg_parse` embeds `struct reg_format_callback` first so it can be used as a formatter writer. Public APIs are `reg_parse_new()`, `reg_parse_line()`, `reg_parse_fd()`, `reg_parse_file()`, and `reg_parse_set_options()`. Internal state values are `STATE_DEFAULT`, `STATE_KEY_OPEN`, `STATE_VAL_HEX_CONT`, and `STATE_VAL_SZ_CONT`. Primitive parsers include `srprs_key()`, `srprs_val_name()`, `srprs_val_dword()`, `srprs_val_sz()`, `srprs_val_hex()`, `srprs_val_hex_values()`, and comment/eol helpers.

## Control Flow
`reg_parse_line()` first handles continuation states, then recognizes empty lines, key lines, comments, a first-line header, or value assignments. Values are valid only after a key has opened. DWORDs are packed little-endian into the value buffer, quoted strings are converted from Unix to UTF-16LE with terminator, and hex values can continue over multiple lines. `reg_parse_fd()` reads bytes, guesses or applies file encoding, converts chunks to Unix charset, extracts complete lines, and feeds them to `reg_parse_line()`.

## State And Persistence
Parser state is transient and talloc-owned. It tracks current key, value name/type/blob, line number, return code, flags, and an optional converter for non-UTF-16 encoded string payloads. It does not persist registry changes; callbacks decide what to store.

## Dependencies And Integration Points
The file depends on `cbuf`, `srprs`, `reg_parse_internal`, `reg_parse.h`, `reg_format.h`, POSIX file APIs, and Samba iconv wrappers. It integrates with `reg_import.c` for mutation and `reg_format.c` for round-trip conversion.

## Risks And Test Signals
This is a high-risk parser surface. Tests should cover malformed lines, trailing garbage, values before keys, headers, comments, key deletes, default values, value deletes, DWORD endian encoding, empty and continued hex lists, continued quoted strings, file encodings with BOM/no BOM, chunk boundaries in `reg_parse_fd()`, fail-level behavior, and conversion failures. Fuzzing line parser primitives would be useful because they manipulate shared `cbuf` state.
