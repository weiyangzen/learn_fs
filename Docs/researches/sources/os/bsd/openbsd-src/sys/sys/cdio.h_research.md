# File Research: sources/os/bsd/openbsd-src/sys/sys/cdio.h

This header defines CD-ROM and DVD ioctl ABI structures and command constants shared between kernel and userland.

Key definitions:
- CD addressing/layout types: `union msf_lba`, `struct cd_toc_entry`, subchannel header/data structures, and `struct cd_sub_channel_info`.
- CD ioctls: play by track/block/MSF, read subchannel, read TOC header/entries, read multisession address, volume/patch control, pause/resume/reset/start/stop/eject/lock/unlock/close, and load/unload.
- DVD structures: `struct dvd_layer`, `dvd_physical`, `dvd_copyright`, `dvd_disckey`, `dvd_bca`, `dvd_manufact`, and `union dvd_struct`.
- DVD authentication ABI: authentication state constants and `union dvd_authinfo`.

Behavior and integration:
- Includes `<sys/types.h>` and `<sys/ioccom.h>`.
- Uses `_BYTE_ORDER` to define CD bitfields consistently for little- and big-endian machines.
- Ioctl numbers use command groups `'c'` for CD and `'d'` for DVD.

Risk notes:
- Several structs contain user pointers passed through ioctls, so kernel handlers must validate lengths and copy boundaries.
- `CDIOCPLAYMSF` and `CDIOCALLOW` share command number 25 under different historical layouts; compatibility handling depends on ioctl encoding including direction/size.
