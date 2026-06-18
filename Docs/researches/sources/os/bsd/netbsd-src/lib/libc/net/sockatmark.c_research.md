# File Research: sources/os/bsd/netbsd-src/lib/libc/net/sockatmark.c

Implementation of `sockatmark()`. It asserts the socket descriptor is not `-1`, issues `ioctl(s, SIOCATMARK, &val)`, and returns either `-1` on ioctl failure or the returned at-mark value.

This is a thin libc wrapper around the socket ioctl.
