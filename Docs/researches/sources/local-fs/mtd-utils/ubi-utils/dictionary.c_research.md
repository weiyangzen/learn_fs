# File Research: sources/local-fs/mtd-utils/ubi-utils/dictionary.c

## Role
Vendored iniparser dictionary implementation for string key/value storage.

## Main Behavior
- Provides hash computation, allocation, deletion, lookup, set, unset, and dump operations.
- Stores keys, values, and hash values in parallel arrays.
- Doubles storage when full.
- Duplicates key/value strings into owned memory.

## Interfaces And Dependencies
- Implements declarations from `include/dictionary.h`.
- Used by `libiniparser.c`.

## Notes
- `mem_double()` can lose original pointers if one of several reallocations fails after assignment.
- API uses non-const `char *` parameters for keys/values, reflecting old upstream style.
