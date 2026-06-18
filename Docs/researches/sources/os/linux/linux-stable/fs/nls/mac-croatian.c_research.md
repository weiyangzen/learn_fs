# File Research: sources/os/linux/linux-stable/fs/nls/mac-croatian.c

## Purpose
Implements the `maccroatian` NLS table for one-byte Mac Croatian filename charset conversion.

## Origin and License
Generated from Unicode Organization charset data. Includes the Unicode data permission notice and declares `MODULE_LICENSE("Dual BSD/GPL")`.

## Data Tables
- `charset2uni[256]` maps Mac Croatian bytes to Unicode, including Croatian-specific Latin characters and the private-use Apple logo mapping at `0xf8ff`.
- Reverse Unicode-to-charset pages:
  - `page00`
  - `page01`
  - `page02`
  - `page03`
  - `page20`
  - `page21`
  - `page22`
  - `page25`
  - `pagef8`
- `page_uni2charset[256]` points high Unicode bytes to these tables.
- `charset2lower[256]` and `charset2upper[256]` are generated sentinel tables.

## Conversion Functions
- `uni2char()` uses the high-byte page table and low-byte index for exact mappings only.
- `char2uni()` indexes the byte-to-Unicode table directly.
- Both functions process a single character and return either `1` or a negative errno.

## Registration
- Charset name: `"maccroatian"`.
- Init function registers the NLS table.
- Exit function unregisters it.
- Module description is `NLS Codepage maccroatian`.

## Research Notes
This module is selected by `CONFIG_NLS_MAC_CROATIAN` and built as `mac-croatian.o`. Its only behavior beyond registration is exact table lookup.
