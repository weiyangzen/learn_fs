# File Research: sources/os/linux/linux/fs/smb/client/winucase.c

## Scope
Read completely: 649 lines. This file is a generated/static Windows-compatible UTF-16 uppercase mapping table plus one lookup function.

## Purpose
`winucase.c` implements `cifs_toupper()`, a Unicode uppercase conversion helper matching Microsoft’s Windows 8 uppercase mapping table. SMB clients need Windows-compatible case folding for case-insensitive comparisons and name handling.

## Data Structure
The file defines second-level 256-entry mapping tables for selected high-byte ranges:
- `t2_00`
- `t2_01`
- `t2_02`
- `t2_03`
- `t2_04`
- `t2_05`
- `t2_1d`
- `t2_1e`
- `t2_1f`
- `t2_21`
- `t2_24`
- `t2_2c`
- `t2_2d`
- `t2_a6`
- `t2_a7`
- `t2_ff`

`toplevel[256]` maps the high byte of a UTF-16 code unit to one of those second-level tables or `NULL`.

## Main Interface
`wchar_t cifs_toupper(wchar_t in)`:
- Extracts the upper byte of the input code unit.
- Looks up the relevant second-level table in `toplevel`.
- If no table exists, returns the original input.
- Extracts the lower byte and reads the mapped uppercase code unit.
- If the table entry is nonzero, returns it; otherwise returns the original input.

## Source And Generation
Comments state the tables were converted from Microsoft’s documented Windows 8 uppercase mapping table using `winucase_convert.pl`. This explains why the data is table-driven rather than using generic kernel NLS case conversion.

## Integration Points
The helper is part of CIFS Unicode handling and is used by name comparison/hash code that needs Windows/SMB-compatible uppercase behavior. It includes `<linux/nls.h>` and exposes a prototype before the definition to quiet sparse.

## Notable Behaviors
- Only single UTF-16 code units are mapped; this is not full Unicode case folding with multi-codepoint expansions.
- Zero in a table means “no mapping”; it does not map to NUL.
- Most high-byte ranges have no table and therefore return identity.
- ASCII lowercase maps to uppercase through `t2_00`.
- Latin, Greek, Cyrillic, Armenian, Georgian, enclosed alphanumerics, Glagolitic/Coptic-style ranges, Latin Extended ranges, and fullwidth ASCII ranges are represented where present in the Windows table.

## Risks And Review Focus
- The table must remain synchronized with SMB/Windows semantics, not necessarily Linux locale behavior.
- Because zero means no mapping, the data generator must avoid encoding any real uppercase mapping to codepoint zero.
- `wchar_t` width assumptions matter; this operates on 16-bit-style code units in SMB Unicode paths.
- Manual edits to the table are risky; regeneration from a known source is safer.

## Research Takeaways
`winucase.c` is a deterministic compatibility table. The logic is simple, but the data is protocol-important because case-insensitive SMB name behavior should match Windows servers closely.
