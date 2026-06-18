# File Research: sources/local-fs/mtd-utils/ubi-utils/include/ubiutils-common.h

## Role
Small shared utility header for UBI user tools.

## Main Contents
- Declares byte-string parsing, byte printing, wrapped text printing, and random seeding helpers:
  - `ubiutils_get_bytes`
  - `ubiutils_print_bytes`
  - `ubiutils_print_text`
  - `ubiutils_srand`

## Interfaces And Dependencies
- C/C++ compatible declarations.
- Used by tools such as `mtdinfo`, `ubiattach`, and `ubiformat`.

## Notes
- This header only declares helpers; implementations are outside this file group.
