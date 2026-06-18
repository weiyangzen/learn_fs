# sources/user-network-fs/samba/source4/lib/registry/util.c

## Purpose

`util.c` provides registry value display/parsing helpers and absolute-path convenience operations over registry contexts.

## Important APIs, Types, and Functions

`reg_val_data_string()` converts typed `DATA_BLOB` values to printable strings. `reg_val_description()` formats `name = type : value`. `reg_string_to_val()` parses command/dotreg-like type and data strings into winreg type ids and blobs. Internal `reg_strhex_to_data_blob()` parses comma-tolerant hex bytes. Path helpers include `reg_open_key_abs()`, `get_abs_parent()`, `reg_key_del_abs()`, and `reg_key_add_abs()`.

## Control Flow

Display helpers switch on winreg type. String values are converted from UTF-16 to Unix charset, DWORD/QWORD values are formatted as hex, binary is upper hex, and unsupported or REG_NONE types may return NULL. Parsing first resolves the type string through `regtype_by_string()` or Windows textual forms (`hex(...)`, `hex`, `dword`), then converts data according to the resulting type. Absolute path helpers split the predefined root from the rest of a backslash-delimited path, open the root, then open/create/delete the final component.

## State and Persistence Behavior

Formatting is read-only and allocates result strings under the caller's talloc context. Parsing allocates blobs under the caller's context. `reg_key_del_abs()` and `reg_key_add_abs()` mutate the target registry context by deleting or creating keys; `reg_open_key_abs()` only returns a key.

## Dependencies and Integration Points

The file depends on `registry.h`, winreg constants, Samba charset conversion, data blob helpers, byte-order macros, and talloc. It is used by CLI tools (`regshell`, `regtree`), Python `str_regtype()` indirectly, diff code, and tests in `tests/generic.c` and `tests/registry.c`.

## Risks and Edge Cases

`REG_MULTI_SZ` formatting is not implemented. `REG_DWORD_BIG_ENDIAN` display and parsing use little-endian `IVAL`/`SIVAL`, so semantic big-endian handling is questionable. `reg_strhex_to_data_blob()` allocation length is approximate and ignores separators by scanning hex pairs; malformed input can truncate silently. Absolute path helpers return generic `WERR_FOOBAR` for missing backslashes and do not use the `access_mask` argument in `reg_key_add_abs()`.

## Test Signals

`tests/generic.c` covers several display paths and `tests/registry.c` covers absolute add and key operations. Missing but valuable tests include `reg_string_to_val()` for all supported type strings, invalid hex, `hex(type)`, QWORD, REG_NONE, REG_MULTI_SZ expectations, and absolute delete.

Source-read signal: reviewed complete local file (302 lines).
