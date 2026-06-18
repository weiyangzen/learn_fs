# File Research: sources/os/linux/linux-stable/fs/nls/mac-centeuro.c

## Purpose
Implements the `maccenteuro` NLS table for one-byte Mac Central European filename charset conversion.

## Origin and License
Generated from Unicode Organization charset tables. Includes the Unicode permission notice and declares `MODULE_LICENSE("Dual BSD/GPL")`.

## Data Tables
- `charset2uni[256]` maps bytes to Unicode, with Central European accented Latin mappings.
- Reverse Unicode-to-charset pages:
  - `page00`
  - `page01`
  - `page02`
  - `page20`
  - `page21`
  - `page22`
  - `page25`
- `page_uni2charset[256]` links Unicode high bytes to these page tables.
- `charset2lower[256]` and `charset2upper[256]` are present for NLS table completeness and contain generated sentinel values.

## Conversion Functions
Same contract as the other generated Mac NLS modules:
- `uni2char()` emits one byte, returns `1`, or fails with `-ENAMETOOLONG`/`-EINVAL`.
- `char2uni()` consumes one byte, returns `1`, or fails if the table maps to `0x0000`.

## Registration
- Charset name: `"maccenteuro"`.
- Init registers the table with `register_nls()`.
- Exit unregisters it with `unregister_nls()`.
- Module description is `NLS Codepage maccenteuro`.

## Research Notes
The distinguishing content is the table data, not the control flow. This module supports Mac Central European encodings selected by `CONFIG_NLS_MAC_CENTEURO`.
