# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_iso8859-2.c

This file registers ISO-8859-2 as `iso8859-2`, covering Central and Eastern European Latin characters.

The structure matches the other generated NLS files: `charset2uni[256]`, reverse lookup pages `page00`, `page01`, `page02`, case conversion tables, `uni2char`, `char2uni`, and a static `nls_table`.

The reverse mapping includes Latin Extended-A and modifier-letter entries used by ISO-8859-2. Exact mappings only are accepted; missing or ambiguous Unicode input returns `-EINVAL`.

Case folding is byte-table based, not Unicode algorithm based. It maps charset bytes to their single-byte lower/upper equivalents and leaves unsupported cases unchanged.

Research notes: no dynamic state and no filesystem-specific logic; correctness depends entirely on the static tables matching the intended code page.
