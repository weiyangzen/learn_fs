# File Research: sources/os/plan9/plan9/sys/src/cmd/cpp/tokens.c

Token-row storage, rewriting, whitespace, and output routines for `cpp`.

It allocates/grows token rows, compares macro definitions, inserts replacement rows, shifts token ranges, normalizes token rows by copying token text, and creates explicit whitespace when adjacent tokens could merge. `puttokens` coalesces contiguous source spans into an output buffer and suppresses normal output under dependency-generation mode.

It also provides debug token printing, newline-only row creation, decimal output formatting, and `newstring` allocation with optional leading-space offset.
