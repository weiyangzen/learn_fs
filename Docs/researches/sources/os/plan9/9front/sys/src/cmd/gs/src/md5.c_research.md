# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/md5.c

## Purpose
Standalone independent MD5 implementation derived from RFC 1321 concepts, exposing init/append/finish digest operations.

## Main Structure
- Includes `md5.h` and `<string.h>`.
- Determines byte order statically via `ARCH_IS_BIG_ENDIAN` or dynamically at runtime.
- Defines MD5 constants `T1` through `T64`.
- `md5_process` processes one 64-byte block through MD5 rounds F, G, H, and I.
- `md5_init` initializes count and digest state.
- `md5_append` updates bit count, buffers partial blocks, and processes full 64-byte blocks.
- `md5_finish` pads the message, appends length, and writes the 16-byte digest.

## Integration Notes
- Built specially in `lib.mak` to prepend Ghostscript memory header handling before compiling generated `md5.c`.
- Used by stream digest support through `smd5.dev`.

## Risks and Edge Cases
- `md5_append` takes `int nbytes`; very large single append lengths are limited by signed integer range, though total count is stored in two 32-bit words.
- Uses pointer alignment arithmetic through `data - (const md5_byte_t *)0`, a historical idiom that can be compiler-sensitive.
- MD5 is cryptographically broken for collision resistance; suitable only for legacy checksums/digests where security is not required.
