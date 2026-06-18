# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_gb2312.h

## Purpose
Provides the kernel iconv mapping table for converting UTF-8 encoded code points to GB2312 byte values.

## Main Interfaces
- `KICONV_UTF8_GB2312_MAX`: declares the maximum mapping count as `7451`.
- `kiconv_utf8_gb2312[]`: static `kiconv_table_t` table, available only under `_KERNEL`.
- Entries encode UTF-8 byte sequences as packed integer keys and GB2312 byte pairs as integer values.
- Includes a fallback-style first entry mapping `0x0000` to `0x003F`.

## Dependencies And Relationships
This header assumes `kiconv_table_t` has already been defined by the including kernel conversion code. It is a generated/static data asset consumed by the kernel character conversion subsystem rather than a standalone API.

## Research Notes
The file is almost entirely data. It carries both CDDL/Sun copyright and Unicode data license text, and notes Sun modifications. The table includes punctuation, Greek, Cyrillic, kana, bopomofo, symbols, CJK ideographs, and fullwidth forms covered by the GB2312 mapping.
