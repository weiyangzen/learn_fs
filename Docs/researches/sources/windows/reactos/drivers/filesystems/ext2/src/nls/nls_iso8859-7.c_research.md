# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_iso8859-7.c

This module registers ISO-8859-7 Greek as `iso8859-7`.

The byte-to-Unicode table maps Greek tonos, uppercase/lowercase Greek letters, final sigma, diaeresis variants, and selected punctuation. Reverse lookup uses `page00`, `page02`, `page03`, and `page20`.

Case tables include Greek-specific byte mappings, including uppercase/lowercase Greek letters and accented variants where representable in the charset.

The conversion functions are the same exact-table pattern as the other NLS modules: one output byte per accepted Unicode character, one Unicode character per input byte, and `-EINVAL` for unmapped/sentinel entries.

Research notes: static table implementation with no filesystem-specific control flow; undefined code points are rejected rather than substituted.
