# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/imagefile.h

## Purpose
Shared interface for the Plan 9 image conversion suite.

## Key Types
Defines `Rawimage`, which carries rectangle, optional colormap, channel count, up to four channel buffers, channel descriptor, channel length, and format-specific GIF fields.

## Channel Descriptors
Defines internal descriptors such as `CRGB`, `CYCbCr`, `CY`, `CRGB1`, `CRGBV`, `CRGB24`, `CRGBA32`, `CYA16`, and `CRGBVA16`.

## API Surface
Declares readers for JPEG/PNG/GIF/PPM, conversion helpers `torgbv` and `totruecolor`, raw writer, GIF/PPM/PNG writers, and single/multi-channel conversion helpers.
