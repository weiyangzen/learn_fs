# File Research: sources/os/linux/linux/io_uring/advise.h

## Purpose
Declares io_uring advise opcode prep and issue functions.

## Main Contents
- Prototypes for `io_madvise_prep()`, `io_madvise()`, `io_fadvise_prep()`, and `io_fadvise()`.

## Cross-File Relationships
- Implemented by `advise.c`.
- Consumed by io_uring opcode dispatch definitions.

## Risks / Review Notes
- No include guard is present; this matches small local io_uring headers but should be preserved only if include patterns remain simple.
