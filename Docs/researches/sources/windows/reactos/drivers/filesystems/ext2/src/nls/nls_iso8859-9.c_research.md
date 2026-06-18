# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_iso8859-9.c

This file registers ISO-8859-9 as `iso8859-9`, the Turkish Latin-5 charset.

The mapping is mostly ISO-8859-1-like, with Turkish-specific entries for G-breve, dotted capital I, dotless small i, and S-cedilla. Reverse lookup uses `page00` and `page01`.

Case conversion tables include Turkish byte mappings, including `0xdd` to `0x69` and `0xfd` to `0x49` behavior for dotted/dotless I in this table's byte-level casing.

As with the other NLS modules, `uni2char` only emits exact one-byte mappings and `char2uni` rejects zero/sentinel mappings.

Research notes: callers relying on language-neutral case folding should be aware this table embeds charset-specific Turkish casing behavior.
