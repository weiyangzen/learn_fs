# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libtags/it.c

## Role

This file extracts the title from Impulse Tracker module files.

## Main Interface

`tagit(Tagctx *ctx)` reads the `IMPM` signature plus the 26-byte song name. If the signature matches, it converts the title from ISO-8859-1 to UTF-8 and emits `Ttitle`.

## Risks

The parser only identifies the format and title. It does not parse duration, channels, instruments, or other module metadata.
