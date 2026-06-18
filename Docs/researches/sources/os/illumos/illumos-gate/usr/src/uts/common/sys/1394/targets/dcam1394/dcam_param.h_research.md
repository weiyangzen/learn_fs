# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/targets/dcam1394/dcam_param.h

## Purpose

`dcam_param.h` declares parameter capability discovery and get/set operations for the 1394 digital camera driver.

## Main Interfaces

The header defines repeated capability bits for valid/present/get/set/control-set support, then exposes:

- `param_attr_init()` and `param_attr_set()` for building the parameter capability bitmap.
- ioctl-level `dcam1394_ioctl_param_get()` and `dcam1394_ioctl_param_set()`.
- generic `dcam1394_param_get()` and `dcam1394_param_set()`.
- generic feature CSR helpers `feature_get()` and `feature_set()`.

It also declares per-parameter handlers for power, video mode, frame rate, ring-buffer capacity and counters, frame size, status, and camera image controls such as brightness, exposure, sharpness, white balance, hue, saturation, gamma, shutter, gain, iris, focus, zoom, pan, and tilt.

## Research Notes

This is a function contract, not a data-heavy header. It maps user-visible DCAM parameter lists to camera register access and driver-local state. Correctness depends on matching capability bits to the actual register support exposed by the device.
