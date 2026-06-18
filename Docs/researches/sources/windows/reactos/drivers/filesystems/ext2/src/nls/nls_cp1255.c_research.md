# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp1255.c

Generated Linux NLS module for Windows codepage CP1255, Hebrew. The byte-to-Unicode table covers ASCII/control bytes, Windows punctuation, shekel sign, Hebrew vowel marks, punctuation, Hebrew letters, and selected undefined byte slots. Reverse Unicode mapping pages are `00`, `01`, `02`, `05`, `20`, and `21`.

The file uses the shared single-byte NLS conversion structure. `uni2char` looks up an exact reverse mapping from `page_uni2charset`; `char2uni` maps the input byte through `charset2uni`; both reject zero/unmapped values. The case tables mostly leave Hebrew bytes unchanged while preserving ASCII case conversion and the mappings present in the generated table.

The module registers charset `"cp1255"` and alias `"iso8859-8"`, and it declares `MODULE_ALIAS_NLS(iso8859-8)`. Init and exit functions register/unregister the table with the NLS base layer.
