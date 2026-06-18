# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/todio.h

## Purpose
TOD device ioctl command definitions.

## Main Interfaces
- Defines ioctl base `TOD_IOC`.
- Defines commands `TOD_GET_DATE`, `TOD_SET_ALARM`, and `TOD_CLEAR_ALARM`.

## Dependencies And Relationships
Used by time-of-day clock drivers and consumers issuing TOD device ioctls.

## Research Notes
This header only defines command numbers; payload structure is determined by the driver-side ioctl implementation.
