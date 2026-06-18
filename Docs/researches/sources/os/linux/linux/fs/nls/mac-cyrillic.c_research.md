# File Research: sources/os/linux/linux/fs/nls/mac-cyrillic.c

Implements the `maccyrillic` NLS codepage module.

Main structure:
- Generated Mac Cyrillic translation tables.
- `charset2uni[256]` maps bytes `0x80` onward heavily into Cyrillic Unicode ranges, with additional punctuation and symbols.
- Reverse Unicode-to-charset pages include `0x00`, `0x01`, `0x04`, `0x20`, `0x21`, and `0x22`.
- Case conversion arrays are present but sentinel-filled.
- `uni2char()` performs exact page-table reverse mapping.
- `char2uni()` maps single bytes to Unicode and rejects Unicode zero.
- Registers as charset `maccyrillic`.

Lifecycle:
- `init_nls_maccyrillic()` registers the table.
- `exit_nls_maccyrillic()` unregisters it.
- Module description is `NLS Codepage maccyrillic`; license is `Dual BSD/GPL`.

Risk notes:
- Exact mapping behavior means Cyrillic compatibility variants outside the table are not accepted.
- The table includes Euro and Cyrillic extension mappings, so changes should be validated against source Unicode mapping data rather than edited manually.
