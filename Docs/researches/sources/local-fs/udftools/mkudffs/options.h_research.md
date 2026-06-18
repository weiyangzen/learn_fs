# File Research: sources/local-fs/udftools/mkudffs/options.h

## Role

Option token definitions and parser declarations for `mkudffs`.

## Contents

- Declares `usage()` and `parse_args()`.
- Defines numeric option IDs split by range:
  - `0x1000` range for no-argument long switches.
  - `0x2000` range for required-argument settings.
- Covers help, charset options, media/VAT/new-file/no-write/read-only switches, and all label/layout/media/accounting options.

## Dependencies

Requires `struct udf_disc` to be visible to callers through included `mkudffs.h` or compatible forward context.

## Research Notes

Keep token values stable relative to `options.c`; parser switch cases depend directly on these constants.
