# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libtags/xm.c

## Role

This file extracts the title from FastTracker XM module files.

## Main Interface

`tagxm(Tagctx *ctx)` reads the `Extended Module: ` signature and following 20-byte title. If the signature matches, it converts the title from CP437 to UTF-8 and emits `Ttitle`.

## Risks

The parser only validates the leading signature and title field. It does not parse full XM structure or duration.
