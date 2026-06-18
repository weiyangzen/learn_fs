# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/serial/prolific.c

## Role

Implements the Prolific PL2303 USB serial backend for `nusb/serial`.

## Main Behavior

The file defines PL2303 chip revisions, class/vendor request constants, status bits, device control register values, pipe reset requests, and a broad VID/PID table for Prolific chips and rebadged phone/GPS/serial cables.

`plprobe` matches the device ID, marks that an interrupt endpoint is required, and installs `plops`.

`plinit` classifies the chip as H, HX, or unknown using revision ID and Linux-derived heuristics, runs the vendor initialization sequence, initializes DCR registers, reads line parameters, and starts a status reader process.

`plgetparam` and `plsetparam` use CDC line coding requests to read/write baud, stop bits, parity, and data bits. Unsupported 1.5 stop-bit state is reported as a warning.

## Status And Recovery

The interrupt endpoint is read by `statusreader` through `plreadstatus`. Status bytes update DCD, DSR, CTS, ring, and framing/parity/overrun counters. Non-timeout read errors call `serialrecover`.

`plclearpipes` uses vendor pipe reset requests for HX devices and endpoint unstalling for older variants.

## Integration Points

`plops` provides initialization, get/set parameters, pipe clearing, line control, hardware flow control, break control, max-packet setup, and generic endpoint discovery.

## Notable Details

The implementation distinguishes hardware flow-control bit patterns for H and HX variants. It also limits endpoint max packet size to 256 bytes because of output size encoding constraints.
