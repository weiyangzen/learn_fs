# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp437.c

Generated Linux NLS module for DOS codepage CP437. It maps bytes to Unicode for ASCII, Western European accented letters, box-drawing characters, block elements, Greek/math symbols, and other original IBM PC glyphs. Reverse Unicode maps are provided for pages `00`, `01`, `03`, `20`, `22`, `23`, and `25`.

The conversion routines implement exact one-byte mapping only. `uni2char` uses the Unicode high byte to choose a reverse page table and the low byte to select a codepage byte; `char2uni` returns the corresponding wide character from `charset2uni`. Both use `-EINVAL` for missing mappings and `uni2char` also checks output length.

The table is registered under charset `"cp437"` with no alias. The lower/upper tables include ASCII folding and generated folding for CP437 accented Latin entries where a byte-level uppercase/lowercase counterpart exists.
