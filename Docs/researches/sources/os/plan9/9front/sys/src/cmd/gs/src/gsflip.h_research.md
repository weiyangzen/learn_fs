# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsflip.h

## Role

`gsflip.h` declares the planar-to-chunky image sample conversion API implemented by `gsflip.c`.

This is image layout infrastructure, not filesystem code.

## Public API

- `image_flip_planes(byte *buffer, const byte **planes, int offset, int nbytes, int num_planes, int bits_per_sample)`

## Contract

The header documents that input starts at `planes[i] + offset`, output is written to `buffer`, input must contain an integral number of pixels, and valid sample depths are 1, 2, 4, 8, and 12 bits/sample.

Returns `0` on success and `-1` for invalid arguments.
