# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_utf7.h

## Scope

Public header for the Citrus UTF7 encoding module.

## APIs

- Defines include guard `_CITRUS_UTF7_H_`.
- Declares ctype and stdenc getops functions for `UTF7`.

## Dependencies And Invariants

- Exposes no conversion state or constants; all UTF-7 behavior is template-backed implementation detail.
