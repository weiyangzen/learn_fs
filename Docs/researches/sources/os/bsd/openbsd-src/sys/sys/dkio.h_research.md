# File Research: sources/os/bsd/openbsd-src/sys/sys/dkio.h

This header defines disk-specific ioctl commands.

Key definitions:
- Disklabel ioctls: `DIOCGDINFO`, `DIOCSDINFO`, `DIOCWDINFO`, `DIOCGPART`, `DIOCGPDINFO`, `DIOCRLDINFO`.
- Removable/cache ioctls: `DIOCEJECT`, `DIOCLOCK`, `DIOCINQ`, `DIOCGCACHE`, `DIOCSCACHE`, `DIOCCACHESYNC`.
- Disk mapping ioctl: `DIOCMAP`.
- Compatibility transition sizing: `O_disklabel`, `O_DIOCGDINFO`.
- Structures: `dk_inquiry`, `dk_cache`, `dk_diskmap`.

Behavior and integration:
- Includes `<sys/ioccom.h>`.
- References `struct disklabel` and `struct partinfo` from disklabel definitions.

Risk notes:
- `dk_diskmap` includes a user pointer and fd; ioctl handlers must validate both.
- `O_DIOCGDINFO` exists for transition from 16 to more partitions and is ABI-compatibility sensitive.
