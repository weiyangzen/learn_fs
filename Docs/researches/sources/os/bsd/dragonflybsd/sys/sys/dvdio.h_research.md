# File Research: sources/os/bsd/dragonflybsd/sys/sys/dvdio.h

DVD structure and CSS/RPC authentication ioctl ABI.

Key responsibilities:
- Defines `struct dvd_layer` for physical layer metadata including book type/version, size/rate, layers, path/type, density, BCA, and sector bounds.
- Defines `struct dvd_struct` for READ DVD STRUCTURE requests with format, layer, copy-management fields, length, and 2048-byte data buffer.
- Defines `struct dvd_authinfo` for REPORT KEY/SEND KEY operations, including AGID, ASF/CPM/CP_SEC/CGMS flags, region/RPC data, LBA, and key/challenge buffer.
- Defines DVD structure format constants, report-key/send-key format constants, AGID invalidate value, and ioctls for report key, send key, and read structure.

Dependencies:
- Includes `sys/types.h` and `sys/ioccom.h`.

Notable risks:
- Bitfield layout and ioctl struct ABI must match driver/userland expectations.
- Authentication operations are stateful around AGID and media region/RPC data.
