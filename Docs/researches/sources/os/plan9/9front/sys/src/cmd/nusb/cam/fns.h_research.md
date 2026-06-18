# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/cam/fns.h

This header declares cross-file functions for the UVC camera driver. It exposes control read/write entry points, descriptor and probe-control printers, streaming lifecycle functions (`videoopen`, `videoclose`, `videoread`, `videoflush`), and `getframedesc()` for resolving the active format/frame indices.

The declarations define the narrow coupling between the 9P camera frontend, the UVC control implementation, descriptor diagnostics, and the video conversion/streaming implementation.
