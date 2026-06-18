# sources/user-network-fs/samba/source3/registry/reg_parse_internal.h

## Purpose
`reg_parse_internal.h` declares shared private helpers for registry parser/formatter code and abstracts native iconv use when available.

## Important APIs, Types, And Functions
It conditionally maps `smb_iconv_t`, `smb_iconv`, `smb_iconv_open`, and `smb_iconv_close` to native iconv symbols. It declares `iconvert_talloc()`, `struct hive_info`, external hive constants, `HIVE_INFO[]`, `hive_info()`, `srprs_hive()`, `smbreg_get_charset()`, `set_iconv()`, `srprs_option()`, `write_bom()`, `srprs_bom()`, `enum fmt_case`, and `cbuf_puts_case()`.

## Control Flow
Consumers use these APIs to set up encoding conversion, parse options and hive names, emit or consume BOMs, and format text case while writing to `cbuf`.

## State And Persistence
The header declares static metadata exported by the implementation but contains no mutable state. Converter state is owned by callers through `smb_iconv_t` handles.

## Dependencies And Integration Points
It includes `includes.h` and `system/iconv.h` and forward-declares `struct cbuf`. It is intentionally private to the parser/formatter implementation family, not a general registry API.

## Risks And Test Signals
Conditional iconv macro behavior should be compile-tested with native and Samba iconv configurations. API tests should cover each declared helper through `reg_parse_internal.c`.
