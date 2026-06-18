# File Research: sources/local-fs/e2fsprogs/misc/partinfo.c

`partinfo.c` is a small Linux-oriented utility that prints block device geometry and partition extent information.

Core behavior:
- Requires one or more device paths.
- For each device:
  - opens it read-only,
  - calls `HDIO_GETGEO` to fetch heads, sectors, cylinders, and start,
  - calls `BLKGETSIZE` to fetch size in sectors,
  - prints geometry plus start, size, and end sector.
- Continues to the next device after open/ioctl failures.

Important dependencies:
- Linux `hdreg.h` geometry API.
- `BLKGETSIZE`, locally defined if missing but `_IO` exists.
- NLS and `com_err` setup, though direct `fprintf`/`strerror` is used for errors.

Research notes:
- This is legacy diagnostic tooling around kernel block-device ioctls.
- It is not portable outside Linux-style block device APIs.
- It does not modify devices.
