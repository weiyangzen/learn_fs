# File Research: sources/os/linux/linux/fs/nls/mac-gaelic.c

Implements the `macgaelic` NLS codepage module.

Main structure:
- Generated Mac Gaelic translation tables.
- `charset2uni[256]` includes Mac Roman-like base mappings plus Gaelic/Irish orthography-related Latin Extended and combining-era characters.
- Reverse Unicode-to-charset pages include `0x00`, `0x01`, `0x02`, `0x1e`, `0x20`, `0x21`, `0x22`, and `0x26`.
- Case conversion arrays are present but sentinel-filled.
- `uni2char()` performs exact lookup through `page_uni2charset`.
- `char2uni()` maps one input byte and rejects zero Unicode.
- Registers as charset `macgaelic`.

Lifecycle:
- `init_nls_macgaelic()` registers the table.
- `exit_nls_macgaelic()` unregisters it.
- Module description is `NLS Codepage macgaelic`; license is `Dual BSD/GPL`.

Risk notes:
- Like the other generated Mac NLS modules, the implementation is data-driven and should be regenerated from canonical Unicode tables if mappings need to change.
