<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/token.h -->
# sources/user-network-fs/nfs-utils/utils/mount/token.h

## Purpose

`token.h` declares the tokenizer interface used by the mount option parser.

## Important APIs, types, and functions

It forward-declares `struct tokenizer_state` and declares `init_tokenizer`, `next_token`, `tokenizer_error`, and `end_tokenizer`.

## Control flow

There is no executable logic. The intended lifecycle is initialize, repeatedly call `next_token`, inspect `tokenizer_error`, then free with `end_tokenizer`.

## State and persistence behavior

State is opaque and owned by the tokenizer implementation. Returned tokens are heap strings, while the input string remains unmodified.

## Dependencies and integration points

`parse_opt.c` includes this header to obtain quote-aware comma splitting. The header has no external library dependencies beyond C declarations.

## Risks and edge cases

Callers must free each returned token and must not assume `NULL` means success without checking `tokenizer_error`.

## Test signals

API tests should verify proper lifecycle use and that the header can be included independently by C files needing tokenizer declarations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/token.h -->
