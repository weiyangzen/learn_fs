# sources/user-network-fs/samba/source3/registry/reg_format.c

## Purpose
`reg_format.c` formats registry keys and values as `.reg` file lines. It can write to an arbitrary line callback, act as a `reg_parse_callback`, or write a complete encoded file with headers, optional BOM, and final local-variable comments.

## Important APIs, Types, And Functions
The opaque `struct reg_format` embeds a `reg_parse_callback` as its first field so it can be passed where parser callbacks are expected. Public formatters include `reg_format_new()`, `reg_format_file()`, `reg_format_key()`, `reg_format_value()`, `reg_format_value_delete()`, `reg_format_comment()`, and wrappers for `registry_key`, `registry_value`, and `regval_blob`. Helpers print hives and key segments with configurable case and separators. `reg_format_file_opt()` parses file options such as `regedit4`, `regedit5`, `enc`, `fileenc`, `strenc`, `flags`, `sep`, `head`, `nl`, and `bom`.

## Control Flow
Key formatting emits a blank line and a bracketed key, with `[-key]` for deletes. Value formatting chooses a compact textual form when possible: `REG_SZ` becomes a quoted string if zero-terminated UTF-16 and not forced to hex, `REG_DWORD` becomes `dword:%08x` when the size is four bytes, and other values become hex lists with line continuations. `REG_MULTI_SZ` and `REG_EXPAND_SZ` can be transcoded before hex output when a string encoding is configured.

## State And Persistence
Formatter state includes flags, separator, output callback, and an iconv descriptor from UTF-16. File-backed formatters own `FILE *`, newline bytes, file encoding converter, and close through a talloc destructor. The module writes persistent `.reg` files but does not alter Samba registry storage itself.

## Dependencies And Integration Points
It depends on `cbuf`, `srprs`, `reg_parse_internal`, registry value types, and Samba charset/iconv helpers. It is intentionally symmetric with `reg_parse.c`: a formatter can receive parse callbacks, and parser output can be directed into a formatter for conversion or normalization.

## Risks And Test Signals
Important risks include charset conversion failure, line-continuation correctness over the 76-column threshold, flag confusion (`REG_DWORD` checks `REG_FMT_HEX_SZ` in the code path), and lifecycle of file-backed destructors. Tests should round-trip keys and values through parser and formatter, cover default value `@`, key deletion, value deletion, UTF-16 `REG_SZ`, multi-line hex, custom separators/case, BOM output, and file close behavior.
