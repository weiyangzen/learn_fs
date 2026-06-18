# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/inffast.h

## Purpose
Declares the internal fast inflate decoder.

## Key Elements
Contains a single prototype: `void inflate_fast OF((z_streamp strm, unsigned start));`.

## Behavior/Risks
Explicitly warns applications not to include it directly. This is an internal ABI between inflate implementation files and can change with zlib internals.

## Dependencies
Requires `z_streamp` and `OF` macro definitions from the surrounding zlib headers.
