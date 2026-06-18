# File Research: sources/os/bsd/freebsd-src/sbin/ping/utils.h

Header for ping utility helpers.

Key elements:
- Include guard `UTILS_H`.
- Includes `<sys/types.h>`.
- Declares `u_short in_cksum(u_char *, int);`.

Dependencies:
- Included by checksum tests and checksum users.
