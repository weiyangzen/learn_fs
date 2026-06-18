# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ziodev2.c

## Purpose
Implements Level 2 IODevice parameter operators and the `%null%` device.

## Key Functions
- `null_open()` opens the platform null file for write-only access.
- `zgetdevparams()` serializes IODevice parameters onto the operand stack.
- `zputdevparams()` reads stack parameters, verifies the system-params password, and applies IODevice parameters.

## Important Behavior
- `%null%` accepts only write access.
- Device lookup uses `gs_findiodevice()` on a string operand.
- `.putdevparams` requires `SystemParamsPassword` validation before changing device parameters.
- Parameter lists are managed with stack-param helper APIs.

## Research Notes
IODevice configuration interface for PostScript Level 2.
