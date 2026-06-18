# File Research: sources/os/plan9/9front/sys/src/cmd/disk/sacfs/ssort.h

## Purpose
Declares suffix sorting routines used by the SAC compressor.

## Key Contents
- `ssortbyte()` computes a suffix array for byte buffers with a unique end marker and returns the BWT identity permutation index.
- `ssort()` sorts integer alphabets and can optionally compute shared-prefix lengths.

## Notes
The implementation lives in `ssort6.c` and is tailored for compression preprocessing.
