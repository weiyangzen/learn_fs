# File Research: sources/os/bsd/openbsd-src/sbin/vnconfig/vnconfig.c

This is the `vnconfig` utility for configuring, unconfiguring, and inspecting vnode disk devices.

Key behavior:
- Default action configures a file as a `vnd` device.
- `-l` lists configured vnode devices, defaulting to scanning from `vnd0`.
- `-u` clears a configured device.
- `-t disktype` applies disklabel geometry/type defaults.
- `-k` uses a direct passphrase key; `-K rounds [-S saltfile]` derives a key using PBKDF2 and an optional salt file.
- Warns users to consider softraid crypto when using legacy encrypted vnd options.
- Auto-selects the first available `vndN` if no device is supplied.

Important functions:
- `main()`: option parsing and action dispatch.
- `get_pkcs_key()`: reads passphrase, creates/reads salt file, derives Blowfish-sized key material.
- `getinfo()`: calls `VNDIOCGET` and prints or scans device state.
- `config()`: fills `struct vnd_ioctl` and issues `VNDIOCSET`.
- `unconfig()`: issues `VNDIOCCLR`.
- `usage()`: command syntax.

Filesystem/OS relevance:
- Directly configures block devices backed by regular files.
- Uses OpenBSD device-opening helpers, disklabel defaults, vnode disk ioctls, and secure key cleanup via `explicit_bzero`.
