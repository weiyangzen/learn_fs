# File Research: sources/os/bsd/freebsd-src/sys/sys/timepps.h

FreeBSD implementation of the RFC 2783 Pulse Per Second timing API.

Key responsibilities:
- Defines PPS API version, handle and sequence types, NTP fixed-point timestamp type, PPS timestamp union, normal and feed-forward PPS info records, and PPS parameter record.
- Defines capture, offset, echo, wait/poll, timestamp-format, timestamp-clock, and kernel-consumer constants.
- Defines ioctl argument records for fetch, feed-forward-counter fetch, and kernel-consumer binding.
- Defines `PPS_IOC_*` ioctl numbers for create, destroy, params, capabilities, fetch, kernel bind, and feed-forward counter fetch.
- Under `_KERNEL`, defines `struct pps_state`, ABI/lock flags, and kernel PPS entry points including capture, event, init, ioctl, and `hardpps`.
- In userland, provides inline `time_pps_*` wrappers around ioctls, including timeout handling that maps null timeout to negative timespec fields.

Dependencies:
- Includes `_ffcounter`, `ioccom`, and `time`.

Notable risks:
- PPS timestamp paths are precision-sensitive; wrong clock-format or leap/ffcounter handling can corrupt time discipline.
- Kernel drivers using ABI-aware initialization must set driver ABI and optional mutex state consistently before registration.
