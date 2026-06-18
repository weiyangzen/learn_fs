# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_iso8859-6.c

This is the ISO-8859-6 Arabic NLS module registered as `iso8859-6`.

`charset2uni` contains Arabic punctuation and Arabic letters in the U+0600 range. Notably, byte values `0x30`-`0x39` map to Arabic-Indic digits U+0660-U+0669 in this table, while reverse `page06` maps those Unicode digits back to ASCII digit byte positions.

Many byte positions in the upper half are undefined and represented as zero, causing `char2uni` to reject them.

Case conversion tables are effectively identity or sparse because Arabic has no upper/lowercase transformation in this charset.

Research notes: the digit mapping is a notable behavioral detail for callers expecting ASCII `0`-`9` to round-trip as U+0030-U+0039.
