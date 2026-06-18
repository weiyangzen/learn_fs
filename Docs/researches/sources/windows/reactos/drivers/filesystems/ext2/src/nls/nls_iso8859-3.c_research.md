# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_iso8859-3.c

This is the ISO-8859-3 NLS table module registered as `iso8859-3`, supporting Latin-3/South European mappings.

Several positions in `charset2uni` intentionally map to `0x0000`, representing undefined ISO-8859-3 byte slots. Those bytes are rejected by `char2uni`.

Reverse lookup uses `page00`, `page01`, and `page02`, with sparse entries for Latin Extended and modifier characters. Entries set to zero are treated as unmappable.

Lowercase and uppercase tables include ISO-8859-3-specific pairs, including dotted/dotless I handling by byte value rather than locale-aware Unicode behavior.

Research notes: this is a generated compatibility table; it performs no validation beyond buffer length and table presence.
