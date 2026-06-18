# File Research: sources/windows/dokany/dokan/dokan_vector.h

Internal generic vector API declaration for Dokan C code.

Key responsibilities:
- Defines `DOKAN_VECTOR` with raw item storage, item count, item size, capacity, and stack-allocation flag.
- Declares allocation, free, push, pop, clear, access, count, capacity, and item-size functions.

Important behavior:
- The API stores items by value in contiguous memory; callers pass pointers to item data for copying.
- The same vector type is used both for pointer pools and concrete `WIN32_FIND_DATAW` directory entries.

Dependencies:
- Relies on Windows-style types (`PVOID`, `BOOL`, `VOID`) already available through includers; the header itself does not include Windows headers.

Notable risks:
- Because this is a raw byte-vector API, type safety depends entirely on consistent `ItemSize` use by callers.
- The public struct fields make it possible for callers to mutate invariants directly.
