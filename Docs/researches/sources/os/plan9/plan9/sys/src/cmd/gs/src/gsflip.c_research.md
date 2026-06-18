# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsflip.c

## Role

Converts planar image sample data, used for `MultipleDataSource`, into chunky interleaved pixel data.

## Main Data

Contains specialized converters for 3-plane and 4-plane input at 1, 2, 4, 8, and 12 bits per sample, plus generic N-plane paths for DeviceN-style color data. Uses bit tables, bit transpose macros, and Ghostscript sample-store macros.

## Control Flow

`image_flip_planes` validates bit depth and dispatches by plane count. Optimized routines pack RGB/CMYK-style planar bytes directly; generic N-plane routines extract each sample and write it into the output stream using sample-store helpers.

## Dependencies

Depends on `gx.h`, `gserrors.h`, `gsbitops.h`, `gsbittab.h`, and `gsflip.h`.

## Notes

Unsupported plane/depth combinations return `-1`. Twelve-bit paths assume the input represents an integral number of pixels and operate in 3-byte sample groups.
