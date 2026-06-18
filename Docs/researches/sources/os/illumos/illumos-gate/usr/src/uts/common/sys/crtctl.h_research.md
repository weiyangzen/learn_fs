# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/crtctl.h

## Role

Defines legacy cursor/CRT control command byte constants and video attribute values.

## Command Constants

Includes cursor movement and screen editing commands:

- `ESC`
- `CUP`, `CDN`, `CRI`, `CLE`
- `NL`, `HOME`, `VHOME`, `LCA`, `CRTN`
- Blink, clear, erase, delete, insert, keyboard lock/unlock, tabs, scrolling, segment/protect controls.
- Variable-screen controls: `SVSCN`, `UVSCN`, `DVSCN`.
- Video controls: `SVID`, `CVID`, `DVID`.

## Video Attributes

- `VID_NORM`
- `VID_UL`
- `VID_BLNK`
- `VID_REV`
- `VID_DIM`
- `VID_BOLD`
- `VID_OFF`

## Other Constants

- `BRK`: transmit break.
- `HIQ`: place remainder of write on high-priority queue.

## Research Relevance

A small legacy terminal/control header. Filesystem relevance is minimal, but it may appear in historical TTY/console code paths.
