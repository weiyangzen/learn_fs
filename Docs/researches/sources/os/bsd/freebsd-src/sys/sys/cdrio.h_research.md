# File Research: sources/os/bsd/freebsd-src/sys/sys/cdrio.h

## Purpose
`cdrio.h` defines ioctl structures and constants for CD-R/CD-RW writer control.

## Main Interfaces
- `struct cdr_track` describes track data block type, audio preemphasis, and test-write mode.
- `struct cdr_cue_entry` and `struct cdr_cuesheet` describe cue-sheet entries, session format, session type, and test write behavior.
- Format capacity structures describe available formatting layouts and selected format parameters.
- Ioctls cover blanking, next writable address, writer/track initialization, cue sending, flush, fixation, read/write speed, block size get/set, progress, read format capacities, and formatting.

## Implementation Notes
Data block constants enumerate raw, subchannel, Mode 1/2, XA, reserved, and vendor-specific layouts. Session constants distinguish CD-ROM, CDI, XA, final, multisession, and none/reserved modes.

## Dependencies and Constraints
Includes `sys/ioccom.h`. The header only defines the ABI; driver support varies by optical device capability.
