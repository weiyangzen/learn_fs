# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_utf8.c

This module registers UTF-8 as an NLS charset named `utf8`.

Unlike the single-byte table files, `uni2char` delegates to `utf8_wctomb` and `char2uni` delegates to `utf8_mbtowc`. Failed encoding writes `?` to the output byte and returns `-EINVAL`; failed decoding sets the Unicode output to U+003F and returns `-EINVAL`.

`identity[256]` is initialized at module load and used for both lower and upper case conversion, meaning UTF-8 NLS performs no case mapping at the byte-table layer.

Research notes: this module depends on the shared UTF-8 helper functions in the NLS layer and treats UTF-8 as variable-length only in conversion callbacks, not in case folding.
