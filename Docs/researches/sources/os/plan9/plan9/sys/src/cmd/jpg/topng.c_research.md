# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/topng.c

## Purpose
Converts a Plan 9 image to PNG.

## Behavior
Reads a Plan 9 image from stdin or one file, initializes memdraw, and writes PNG through `memwritepng`.

## Options
`-c` adds a text comment, `-g` adds gamma metadata, and `-t` is accepted but has no effect.

## Note
`ImageInfo II` is stack allocated and not visibly zeroed before option parsing, so callers rely on fields being set only when options are used; this is a potential initialization bug.
