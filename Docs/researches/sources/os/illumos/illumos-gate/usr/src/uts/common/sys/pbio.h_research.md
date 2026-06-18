# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pbio.h

## Purpose
Defines a small ioctl/event interface for a power-button or platform-button monitor device.

## Main Interfaces
- Ioctl base:
  - `PBIOC`
- Ioctls:
  - `PB_BEGIN_MONITOR`
  - `PB_END_MONITOR`
  - `PB_CREATE_BUTTON_EVENT`
  - `PB_GET_EVENTS`
- Event constant:
  - `PB_BUTTON_PRESS`

## Dependencies And Relationships
Standalone public ioctl header. The test suite can use `PB_CREATE_BUTTON_EVENT` to synthesize events.

## Research Notes
The header only defines numeric ABI constants; it does not define an ioctl payload structure.
