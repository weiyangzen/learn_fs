# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/targets/dcam1394/dcam_frame.h

## Purpose

`dcam_frame.h` declares the frame-receive subsystem for the 1394 digital camera driver.

## Interfaces

The functions cover ioctl-triggered receive startup, receive subsystem initialization/finalization, start/stop control, and IXL completion callback handling:

- `dcam1394_ioctl_frame_rcv_start`
- `dcam_frame_rcv_init`
- `dcam_frame_rcv_fini`
- `dcam_frame_rcv_start`
- `dcam_frame_rcv_stop`
- `dcam_frame_is_done`

`dcam_frame_rcv_init()` accepts video mode, frame rate, and requested ring-buffer frame count, indicating this layer builds the capture buffers and IXL program for the selected mode.

## Research Notes

This header is intentionally narrow. Its integration point is `dcam_state_t` from `dcam.h`; the implementation is responsible for turning isochronous completions into readable ring-buffer frames and for safely stopping capture.
