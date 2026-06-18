# File Research: sources/os/linux/linux-stable/fs/nls/mac-celtic.c

## Purpose
Implements the `macceltic` NLS table for one-byte Mac Celtic filename charset conversion.

## Origin and License
The file states it was automatically generated from Unicode Organization charset tables. It includes the Unicode data permission notice and declares `MODULE_LICENSE("Dual BSD/GPL")`.

## Data Tables
- `charset2uni[256]` maps each Mac Celtic byte to a Unicode `wchar_t`.
- Reverse Unicode-to-charset lookup pages:
  - `page00`
  - `page01`
  - `page03`
  - `page1e`
  - `page20`
  - `page21`
  - `page22`
  - `page25`
  - `page26`
- `page_uni2charset[256]` indexes those reverse pages by Unicode high byte.
- `charset2lower[256]` and `charset2upper[256]` are provided to the NLS core. In this generated file they are filled with sentinel values rather than meaningful case conversions.

## Conversion Functions
- `uni2char()`:
  - Rejects zero output space with `-ENAMETOOLONG`.
  - Looks up the Unicode high-byte page and low byte.
  - Returns `-EINVAL` for unmapped Unicode code points.
  - Emits exactly one byte and returns `1` on success.
- `char2uni()`:
  - Maps one raw byte through `charset2uni`.
  - Treats resulting `0x0000` as invalid and returns `-EINVAL`.
  - Returns `1` on success.

## Registration
- Registers `struct nls_table table` with charset name `"macceltic"`.
- `init_nls_macceltic()` calls `register_nls()`.
- `exit_nls_macceltic()` calls `unregister_nls()`.
- Module description is `NLS Codepage macceltic`.

## Research Notes
This is a data-driven module with no filesystem policy. HFS-family code can request the `macceltic` charset through the NLS subsystem, then use the table callbacks for filename byte/Unicode conversion.
