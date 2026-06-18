# File Research: sources/os/bsd/freebsd-src/sys/sys/cdio.h

## Purpose
`cdio.h` defines the shared kernel/userland ioctl ABI for CD-ROM audio, TOC, subchannel, volume, tray, and drive capability operations.

## Main Interfaces
- Address and TOC structures include `union msf_lba`, `struct cd_toc_entry`, subchannel headers, position data, media catalog data, track info, and aggregate subchannel info.
- Play requests support track/index, block range, and minute/second/frame ranges.
- TOC and subchannel ioctls read headers, entries, single entries, and subchannel data.
- Audio controls include patch routing, get/set volume, mono/stereo/mute/left/right, pause/resume/start/stop/reset, pitch, debug toggles, media allow/prevent/eject/close.
- `struct ioc_capability` reports play, routing, and special function capabilities.

## Implementation Notes
The header preserves legacy spellings such as `CDIOCSETSTERIO` alongside corrected aliases. Bitfields in `cd_toc_entry` account for byte order. Pointer-bearing ioctl structures let userland provide output buffers for variable-size TOC/subchannel results.

## Dependencies and Constraints
Includes `sys/ioccom.h`, and userland includes `sys/types.h`. The ABI is old and hardware-oriented, so callers must handle unsupported ioctls and drive capability variation.
