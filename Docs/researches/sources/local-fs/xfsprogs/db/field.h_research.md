# File Research: sources/local-fs/xfsprogs/db/field.h

Purpose: defines the field type enum and field metadata structures used by the `xfs_db` structured print/navigation system.

Key contents:
- `fldt_t` enumerates all registered field types, including AG metadata, attr formats, btrees, CRCs, dinodes, directory v2/v3/shortform fields, quota fields, realtime group fields, superblocks, scalar integers, UUIDs, parent records, and `FLDT_ZZZ` terminator.
- Defines `offset_fnc_t`, `count_fnc_t`, and `size_fnc_t` plus helper macros `OI`, `CI`, `C1`, and `SI`.
- Defines `field_t` with name, field type, offset, count, flags, and next navigation type.
- Field flags:
  - `FLD_ABASE1`
  - `FLD_SKIPALL`
  - `FLD_ARRAY`
  - `FLD_OFFSET`
  - `FLD_COUNT`
- Defines `ftattr_t`, the per-field-type descriptor with print function, format, size, arguments, address callback, and subfields.
- Field attribute flags cover skip-zero, null handling, signedness, dynamic size, skipped names, and empty unions.
- Declares `ftattrtab`, `bitoffset`, `fcount`, `findfield`, and `fsize`.

Interactions:
- Consumed by almost every structured metadata module in `db/`.
- Depends conceptually on `prfnc_t` from `fprint.h` and `adfnc_t` from `faddr.h`.

Risks/notes:
- Enum order must match `ftattrtab` indices; mismatches would break field decoding globally.
