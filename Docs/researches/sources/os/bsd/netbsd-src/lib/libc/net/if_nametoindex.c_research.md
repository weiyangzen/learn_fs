# File Research: sources/os/bsd/netbsd-src/lib/libc/net/if_nametoindex.c

Implementation of `if_nametoindex()`. It first tries a close-on-exec AF_INET datagram socket and `SIOCGIFINDEX` ioctl for the supplied name.

If that path fails, it falls back to `getifaddrs()` and scans AF_LINK entries by name. If no interface matches, it returns `0` and sets `errno` to `ENXIO`.
