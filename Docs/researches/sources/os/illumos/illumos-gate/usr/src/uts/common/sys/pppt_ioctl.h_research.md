# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pppt_ioctl.h

## Purpose
Defines PPPT ioctl versioning, command numbers, and the common ioctl data structure used for daemon door installation and peer messages.

## Main Interfaces
- `PPPT_VERSION_1`
- `PPPT_IOC`: command base.
- `PPPT_INSTALL_DOOR`: installs a door for daemon communication.
- `PPPT_MESSAGE`: passes data from a peer.
- `pppt_iocdata_t`: version, error, door fd, buffer size, and 64-bit buffer address.

## Dependencies And Relationships
Used by PPPT kernel/user control paths that communicate with a daemon and pass peer message buffers.

## Research Notes
The structure uses fixed-width fields and a 64-bit buffer address, making it explicit for ioctl marshalling.
