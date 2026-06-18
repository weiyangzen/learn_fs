# File Research: sources/os/linux/linux-stable/fs/nls/mac-cyrillic.c

## Purpose
Implements the `maccyrillic` NLS table for one-byte Mac Cyrillic filename charset conversion.

## Origin and License
Generated from Unicode Organization charset tables. Includes Unicode’s data/software permission notice and declares `MODULE_LICENSE("Dual BSD/GPL")`.

## Data Tables
- `charset2uni[256]` maps bytes to Unicode Cyrillic and punctuation/symbol code points.
- Reverse Unicode-to-charset pages:
  - `page00`
  - `page01`
  - `page04`
  - `page20`
  - `page21`
  - `page22`
- `page_uni2charset[256]` indexes those reverse pages.
- `charset2lower[256]` and `charset2upper[256]` are generated sentinel tables.

## Conversion Functions
- `uni2char()` supports exact Unicode mappings only, emits one byte, and fails on unmapped code points.
- `char2uni()` maps one raw byte to Unicode and treats `0x0000` as invalid.
- Bounds and mapping errors are returned as standard negative errnos.

## Registration
- Charset name: `"maccyrillic"`.
- `init_nls_maccyrillic()` registers the table.
- `exit_nls_maccyrillic()` unregisters the table.
- Module description is `NLS Codepage maccyrillic`.

## Research Notes
This is the Cyrillic member of the same generated Mac NLS family. The meaningful difference from Latin Mac modules is concentrated in `charset2uni` and `page04`, which cover Cyrillic Unicode block mappings.
