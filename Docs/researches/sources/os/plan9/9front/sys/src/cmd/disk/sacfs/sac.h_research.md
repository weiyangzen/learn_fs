# File Research: sources/os/plan9/9front/sys/src/cmd/disk/sacfs/sac.h

## Purpose
Declares the SAC compressor and decompressor entry points.

## Key Contents
- `int sac(uchar *dst, uchar *src, int blocksize);`
- `int unsac(uchar *dst, uchar *src, int n, int nsrc);`

## Notes
This header is the minimal API shared by the image builder, filesystem server, compressor, and decompressor.
