# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/targets/dcam1394/dcam_reg.h

## Purpose

`dcam_reg.h` defines DCAM 1394 register offsets, masks, and shifts used to read and write camera control/status registers.

## Register Map

The header covers:

- camera initialize register and assert value.
- inquiry registers for video modes, frame rates, basic function support, and feature element support.
- feature inquiry fields for readout, on/off, auto, manual, min value, and max value.
- current frame rate, video mode, video format, ISO channel, camera power, ISO enable, memory save, one-shot, and memory channel registers.
- feature CSR offsets for brightness, exposure, sharpness, white balance, hue, saturation, gamma, shutter, gain, iris, focus, zoom, pan, and tilt.
- feature CSR masks for presence, on/off, auto/manual mode, value fields, and white-balance U/V values.

## Interfaces

`dcam_reg_read()` and `dcam_reg_write()` are the exported helpers for register I/O using `dcam1394_reg_io_t`.

## Research Notes

This header is the low-level binding to the DCAM camera specification. Mistakes in masks/shifts would directly affect camera parameter reporting and control.
