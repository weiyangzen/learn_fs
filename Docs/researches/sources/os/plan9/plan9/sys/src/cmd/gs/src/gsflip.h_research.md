# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsflip.h

## Role

Public interface for planar-to-chunky image data conversion.

## Main API

Declares `image_flip_planes`, which takes an output buffer, source plane array, byte offset, byte count, plane count, and bits per sample.

## Contract

Valid bits per sample are 1, 2, 4, 8, or 12. `num_planes` must be non-negative. The input must represent an integral number of pixels; for 12-bit samples, `nbytes` is rounded to a multiple of 3 by caller convention.

## Dependencies

Requires Ghostscript byte types from surrounding includes.

## Notes

Returns `0` on supported conversion and `-1` for invalid plane count or sample depth.
