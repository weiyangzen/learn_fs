# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp850.c

Generated Linux NLS module for DOS codepage CP850, the multilingual Latin-1 DOS codepage. The forward table maps ASCII/control bytes, Western European accented letters, box-drawing characters, block glyphs, fractions, currency symbols, and punctuation. Reverse Unicode maps are supplied for pages `00`, `01`, `20`, and `25`.

Conversion is exact and single-byte. `uni2char` fails for unmapped Unicode values or zero output capacity, while `char2uni` maps one raw byte and rejects zero mappings. Lowercase and uppercase tables provide byte-level folding for ASCII and supported CP850 Latin pairs.

The file registers charset `"cp850"` with no alias via `init_nls_cp850` and unregisters via `exit_nls_cp850`. Like the other generated NLS modules, it depends on `nls_base.c` for registry and module-reference behavior.
