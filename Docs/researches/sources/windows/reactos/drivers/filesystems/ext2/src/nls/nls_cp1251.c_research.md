# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp1251.c

Generated Linux NLS module for Windows codepage CP1251, primarily Cyrillic. Its `charset2uni` table maps CP1251 bytes to Unicode Cyrillic, punctuation, currency, and Latin/control code points. Reverse mappings are provided for Unicode pages `00`, `04`, `20`, and `21`, with byte case-folding tables for Cyrillic upper/lower pairs and ASCII.

`uni2char` and `char2uni` are the standard single-byte implementations used by these NLS modules: they perform exact mapping only, return `-ENAMETOOLONG` for no output space, return `-EINVAL` for unmapped characters, and consume or emit one byte per successful character.

The module’s `nls_table` is named `"cp1251"` with no alias. Init and exit functions register and unregister the table through the shared NLS registry, and the file uses Linux module metadata declarations.
