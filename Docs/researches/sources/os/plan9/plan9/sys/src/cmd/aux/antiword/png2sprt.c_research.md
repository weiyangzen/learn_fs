# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/png2sprt.c

## Summary
`png2sprt.c` is the RISC OS sprite-side PNG translation stub. It does not decode PNG and instead emits a dummy image placeholder.

## Main Responsibilities
- Defines `bTranslatePNG()` for the sprite conversion build path.
- Returns `bAddDummyImage()` for any PNG input.

## Key Dependencies
Uses `antiword.h` and the generic image placeholder dispatch.

## Filesystem Relevance
No direct filesystem behavior. Parameters include the source file and image offsets, but they are unused.

## Notes
The file documents that PNG-to-sprite conversion was not implemented in this Antiword version.
