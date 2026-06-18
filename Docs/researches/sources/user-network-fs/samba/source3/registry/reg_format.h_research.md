# sources/user-network-fs/samba/source3/registry/reg_format.h

## Purpose
`reg_format.h` declares the public `.reg` formatter API and documents how formatter objects can also serve as parser callbacks.

## Important APIs, Types, And Functions
The header defines opaque `reg_format`, `reg_format_callback_writeline_t`, and `struct reg_format_callback`. It declares constructors `reg_format_new()` and `reg_format_file()`, high-level wrappers for `registry_key`, `registry_value`, and `regval_blob`, low-level `reg_format_key()` and `reg_format_value()`, deletion/comment helpers, and `reg_format_set_options()`. It defines flags `REG_FMT_HEX_SZ`, `REG_FMT_HEX_DW`, `REG_FMT_HEX_BIN`, `REG_FMT_HEX_ALL`, `REG_FMT_LONG_HIVES`, and `REG_FMT_SHORT_HIVES`.

## Control Flow
Consumers create a formatter with a line callback or output file, then call key/value functions. Because the implementation embeds a `reg_parse_callback`, the object can be used as a parser target to re-emit parsed input.

## State And Persistence
The header describes an opaque talloc-owned object. File-backed instances persist formatted registry data to disk; callback-backed instances delegate persistence to the provided writer.

## Dependencies And Integration Points
It forward-declares registry value/key structures and `regval_blob`, avoiding heavier includes for API users. It is paired with `reg_parse.h` for import/export round-trips and with `reg_import.h` for registry API adapters.

## Risks And Test Signals
The macro `REG_FMT_HEX_ALL` includes a trailing semicolon, which can surprise expression users. API tests should compile typical and flag-combination callers. Functional tests should verify documented return conventions, callback error propagation, and talloc ownership expectations.
