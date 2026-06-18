# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/telioctl.h

## Purpose
Defines ioctls and mode bits for the telnet protocol STREAMS module.

## Main Interfaces
- Ioctl base `TELIOC`.
- Ioctls:
  - `TEL_IOC_ENABLE`: resume processing and forward normal data.
  - `TEL_IOC_MODE`: set data-processing mode.
  - `TEL_IOC_GETBLK`: request next network input message while disabled.
- Mode bits:
  - `TEL_BINARY_IN`
  - `TEL_BINARY_OUT`

## Dependencies And Relationships
Related to telnet module control and `logindmux.h` queue exchange behavior referenced in comments.

## Research Notes
The comments define operational semantics, including insertion of attached data at the head of the read queue for `TEL_IOC_ENABLE`.
