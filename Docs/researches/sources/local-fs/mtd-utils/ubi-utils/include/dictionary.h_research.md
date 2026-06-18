# File Research: sources/local-fs/mtd-utils/ubi-utils/include/dictionary.h

## Role
Public header for the vendored dictionary module.

## Main Contents
- Defines `dictionary` with `n`, `size`, `val`, `key`, and `hash` arrays.
- Declares `dictionary_hash`, `dictionary_new`, `dictionary_del`, `dictionary_get`, `dictionary_set`, `dictionary_unset`, and `dictionary_dump`.

## Interfaces And Dependencies
- Includes standard C headers.
- Consumed by `libiniparser.h` and `dictionary.c`.

## Notes
- Documentation explains keys are unique strings and hash comparison is followed by string comparison.
- Uses legacy spelling and formatting from upstream iniparser.
