# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/md5.h

## Role

`private/md5.h` declares libFLAC's MD5 context and functions. FLAC uses MD5 to verify decoded audio stream integrity, not for cryptographic security.

## Contents

It defines `FLAC__multibyte`, a union of byte, int16, and int32 pointers for reusable sample formatting buffers. `FLAC__MD5Context` stores MD5 input block words, state words, byte counters, an internal conversion buffer, and buffer capacity.

It declares `FLAC__MD5Init()`, `FLAC__MD5Final()`, and `FLAC__MD5Accumulate()`.

## Important Contracts

`FLAC__MD5Accumulate()` consumes channel-separated sample arrays and formats them into the canonical byte stream before updating the digest.

## Risks / Edge Cases

The internal buffer is owned by the context and freed during finalization in the implementation. Contexts should be reinitialized before reuse after `Final()`.

## Dependencies

Includes `FLAC/ordinals.h`.
