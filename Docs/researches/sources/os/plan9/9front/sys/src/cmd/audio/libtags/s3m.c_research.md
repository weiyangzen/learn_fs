# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libtags/s3m.c

## Role

This file extracts the title from Scream Tracker 3 module files.

## Main Interface

`tags3m(Tagctx *ctx)` reads the 28-byte title plus two signature/control bytes. It accepts byte 28 as `0x1a` or zero and requires byte 29 to be `0x10`.

## Output

Trailing spaces and NULs are trimmed. The title is converted from CP437 to UTF-8 and emitted as `Ttitle`.

## Risks

The parser performs minimal validation. It does not parse the `SCRM` marker later in the S3M header, so it relies on the initial byte checks used here.
