# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/totruecolor.c

## Purpose
Converts `Rawimage` data to packed truecolor or greyscale output.

## Supported Outputs
Only `CY` and `CRGB24` are accepted.

## Conversion
Handles existing greyscale, indexed-color maps, planar RGB, packed RGB24/RGBA32, YCbCr, and grey-alpha style input. RGB output is in Plan 9 loadimage order; greyscale uses weighted luma conversion where needed. YCbCr-to-RGB uses fixed-point coefficients.

## Output
Returns a new one-channel `Rawimage` with packed bytes and requested descriptor.
