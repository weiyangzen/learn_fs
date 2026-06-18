# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_cck_common.h

## Role

`kiconv_cck_common.h` provides common kernel helpers for CCK-family conversions between UTF-8 and encodings such as GB18030, Big5, EUC-TW, and UHC. Its substantive content is compiled only under `_KERNEL`.

## Major Definitions

The file defines EUC leading-byte rules, ASCII detection, UTF-8 replacement-character bytes and length, and a macro that validates the second byte of three- or four-byte UTF-8 sequences using shared min/max lookup tables. BOM-handling macros skip an initial UTF-8 signature either with conversion state (`KICONV_CHECK_UTF8_BOM`) or without state.

Error macros set `*errno`, mark the return value as `(size_t)-1`, and break, with an alternate path for invalid-input replacement when `KICONV_REPLACE_INVALID` is set. `kiconv_table_t` and `kiconv_table_array_t` represent binary-searchable conversion tables for UTF-8-to-CCK and CCK-to-UTF-8 mappings. `kiconv_utf8tocck_t` is a per-encoding callback used by common wrapper functions.

## Interfaces

The common open/close routines are `kiconv_open_to_cck()` and `kiconv_close_to_cck()`. `kiconv_binsearch()` searches conversion tables. `kiconv_utf8_to_cck()` wraps streaming conversion from UTF-8 to a CCK encoding using an encoding-specific callback, and `kiconvstr_utf8_to_cck()` provides the string-based equivalent. The header also declares UTF-8 validation lookup tables from `u8_textprep.c`.

## Integration Notes

The macros assume local variable names such as `kcd`, `ib`, `ibtail`, `errno`, `ret_val`, and `flag` in conversion implementations, so they are convenient but context-sensitive. Implementations must preserve input/output pointer bounds while using replacement and BOM-skipping paths.
