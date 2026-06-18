# File Research: sources/os/bsd/dragonflybsd/sys/sys/cdio.h

CD-ROM audio, TOC, subchannel, volume, door, and transport ioctl ABI.

Key responsibilities:
- Defines MSF/LBA address union and CD TOC/subchannel data structures.
- Defines audio status values and subchannel payload formats for current position, media catalog, and track info.
- Defines ioctls for playing tracks, blocks, or MSF ranges; reading subchannels and TOC entries; setting audio patches/volume/channel modes; pause/resume/reset/start/stop/eject; allow/prevent removal; and close tray.
- Provides constants for LBA/MSF address formats and sub-Q data formats.

Dependencies:
- Includes `sys/types.h` and `sys/ioccom.h`.

Notable risks:
- Uses bitfields and device protocol layouts; ABI depends on compiler layout compatibility on DragonFly targets.
- Several ioctl payloads contain user pointers that driver implementations must copy safely.
