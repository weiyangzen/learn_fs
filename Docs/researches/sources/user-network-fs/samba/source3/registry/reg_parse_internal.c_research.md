# sources/user-network-fs/samba/source3/registry/reg_parse_internal.c

## Purpose
`reg_parse_internal.c` provides shared helpers for `.reg` parsing and formatting: charset conversion, hive-name metadata and parsing, option parsing, BOM detection/writing, and case-adjusted cbuf output.

## Important APIs, Types, And Functions
`iconvert_talloc()` wraps `smb_iconv()` with talloc allocation and growth. `HIVE_INFO_*` constants and `HIVE_INFO[]` describe short/long hive names and handles. `srprs_hive()` parses short or long hive names, and `hive_info()` resolves a name. `smbreg_get_charset()` maps `dos` and `unix` aliases to loadparm charsets. `set_iconv()` opens/replaces converters. `srprs_option()` parses comma-separated option strings. `srprs_bom()` and `write_bom()` handle BOMs. `cbuf_puts_case()` writes text and applies preserve/upper/lower/title casing.

## Control Flow
Conversion allocates or reuses a destination buffer, retries on `E2BIG`, null-terminates with two zero bytes, and frees on unrecoverable errors. Hive parsing first recognizes `HK...` prefixes, then distinguishes long `HKEY_...` names from short names. Option parsing extracts key/value pairs and advances across commas. BOM handling scans a small static table.

## State And Persistence
The file owns static hive metadata and BOM metadata. It does not persist registry state. `set_iconv()` mutates caller-owned converter handles and closes prior descriptors to avoid leaks.

## Dependencies And Integration Points
It depends on `reg_parse_internal.h`, `cbuf`, `srprs`, `registry.h`, Samba charset configuration, and iconv. It is used by both parser and formatter implementations.

## Risks And Test Signals
Tests should cover conversion growth, invalid byte sequences, closing/replacing converters, each hive short/long spelling, option strings with quotes and missing values, every BOM entry, and casing modes. `srprs_option()` calls `srprs_quoted_string(ptr, ...)` while otherwise using local `pos`, so quoted option parsing should be specifically tested for pointer advancement.
