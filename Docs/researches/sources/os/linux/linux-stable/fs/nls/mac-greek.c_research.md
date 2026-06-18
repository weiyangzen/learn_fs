# File Research: sources/os/linux/linux-stable/fs/nls/mac-greek.c

This file implements the Linux NLS module for the classic Macintosh Greek codepage, registered under charset name `macgreek`.

It is a generated charset translation table module. `charset2uni[256]` maps every single-byte Mac Greek value to Unicode, with ASCII/control bytes preserved for `0x00` through `0x7f` and Greek letters, Greek tonos/dialytika forms, punctuation, symbols, and a few Latin-1 characters in the high half. Reverse conversion is handled through sparse Unicode page tables: `page00`, `page01`, `page03`, `page20`, `page21`, and `page22`, referenced by `page_uni2charset[256]`.

The conversion callbacks follow the common NLS table pattern:
- `uni2char()` checks output capacity, indexes `page_uni2charset` by Unicode high byte, and returns `-ENAMETOOLONG` or `-EINVAL` when the output byte cannot be represented.
- `char2uni()` indexes `charset2uni` by input byte and treats Unicode `0x0000` as unmappable, so NUL is not converted as a normal character.
- `struct nls_table table` binds these callbacks plus `charset2lower` and `charset2upper`.

The case-conversion tables are filled with `0xff` values rather than meaningful ASCII/Greek fold mappings, which means this module primarily provides byte/Unicode translation and should not be expected to implement useful case folding.

Module lifecycle is standard: `init_nls_macgreek()` calls `register_nls(&table)`, `exit_nls_macgreek()` calls `unregister_nls(&table)`, and the file declares `MODULE_DESCRIPTION("NLS Codepage macgreek")` with `Dual BSD/GPL` license. The file also carries the Unicode, Inc. data permission notice.
