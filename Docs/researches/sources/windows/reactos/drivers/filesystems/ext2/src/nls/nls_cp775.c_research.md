# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp775.c

Generated Linux NLS module for DOS codepage CP775, used for Baltic languages. The 256-entry forward table maps ASCII/control bytes, Baltic Latin letters, Western accented letters, punctuation, box-drawing/block characters, and symbols. Reverse mapping pages are `00`, `01`, `20`, `22`, and `25`.

The module follows the common NLS pattern: exact Unicode-to-byte lookup through `page_uni2charset`, exact byte-to-Unicode lookup through `charset2uni`, `-ENAMETOOLONG` on no output space, and `-EINVAL` on unmapped characters. Generated case tables encode ASCII and CP775-specific uppercase/lowercase byte equivalents.

The `nls_table` charset is `"cp775"` with no alias. Init and exit functions register and unregister the table through the shared NLS base code.
