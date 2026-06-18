# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mskanji.h

## Scope

Public header for the Citrus MSKanji encoding module.

## APIs

- Defines include guard `_CITRUS_MSKANJI_H_`.
- Declares ctype and stdenc getops functions through `_CITRUS_CTYPE_GETOPS_FUNC(MSKanji)` and `_CITRUS_STDENC_GETOPS_FUNC(MSKanji)`.

## Dependencies And Invariants

- Provides only module entry declarations; implementation details stay private in the `.c` file.
