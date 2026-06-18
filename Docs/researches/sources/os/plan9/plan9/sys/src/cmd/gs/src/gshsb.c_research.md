# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gshsb.c

## Role

HSB color operators for the Ghostscript library.

## Main Data

Uses fixed-point `frac` arithmetic for RGB/HSB conversion and clamps HSB input components into `[0,1]`.

## Control Flow

`gs_sethsbcolor` clamps hue/saturation/brightness, converts to RGB, and calls `gs_setrgbcolor`. `gs_currenthsbcolor` reads current RGB and converts back to HSB. Internal conversion follows Rogers’ procedural graphics algorithms: RGB-to-HSB finds max/min channels and hue sector; HSB-to-RGB computes sector and intermediate fixed-point values.

## Dependencies

Uses `gx.h`, `gscolor.h`, `gshsb.h`, and `gxfrac.h`.

## Notes

Hue for gray RGB values is arbitrary and returned as zero. Debug logging is available behind the `c` debug flag.
