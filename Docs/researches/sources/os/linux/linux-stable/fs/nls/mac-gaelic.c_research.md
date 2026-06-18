# File Research: sources/os/linux/linux-stable/fs/nls/mac-gaelic.c

## Purpose
Implements the `macgaelic` NLS table for one-byte Mac Gaelic filename charset conversion.

## Origin and License
Generated from Unicode Organization charset tables. Includes the Unicode data permission notice and declares `MODULE_LICENSE("Dual BSD/GPL")`.

## Data Tables
- `charset2uni[256]` maps Mac Gaelic bytes to Unicode, including Gaelic-oriented Latin extended characters and symbols.
- Reverse Unicode-to-charset pages:
  - `page00`
  - `page01`
  - `page02`
  - `page1e`
  - `page20`
  - `page21`
  - `page22`
  - `page26`
- `page_uni2charset[256]` selects these pages by Unicode high byte.
- `charset2lower[256]` and `charset2upper[256]` are generated sentinel tables.

## Conversion Functions
- `uni2char()` requires output space, finds the Unicode page table, and emits one byte for exact mappings.
- `char2uni()` maps one input byte to Unicode.
- Both return `1` for a successful single-character conversion or a negative errno.

## Registration
- Charset name: `"macgaelic"`.
- Init registers with `register_nls()`.
- Exit unregisters with `unregister_nls()`.
- Module description is `NLS Codepage macgaelic`.

## Research Notes
This module is selected by `CONFIG_NLS_MAC_GAELIC` and built as `mac-gaelic.o`. It follows the standard generated NLS module shape used by the other Mac codepage files in this group.
