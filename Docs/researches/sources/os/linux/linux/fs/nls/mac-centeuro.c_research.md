# File Research: sources/os/linux/linux/fs/nls/mac-centeuro.c

Implements the `maccenteuro` NLS codepage module for Central European Macintosh filenames.

Main structure:
- Generated Unicode mapping data.
- `charset2uni[256]` maps the single-byte Central European Mac codepage to Unicode, including many Latin Extended-A characters.
- Reverse Unicode-to-charset pages include `0x00`, `0x01`, `0x02`, `0x20`, `0x21`, `0x22`, and `0x25`.
- Case conversion arrays are present but contain sentinel values rather than active case mappings.
- `uni2char()` performs page-indexed exact reverse lookup.
- `char2uni()` performs byte-indexed forward lookup and rejects Unicode zero.
- Registers as charset `maccenteuro`.

Lifecycle:
- `init_nls_maccenteuro()` registers the table.
- `exit_nls_maccenteuro()` unregisters it.
- Module description is `NLS Codepage maccenteuro`; license is `Dual BSD/GPL`.

Risk notes:
- Only exact mappings are supported. Unicode characters that have visual or compatibility equivalents but no exact table entry return `-EINVAL`.
