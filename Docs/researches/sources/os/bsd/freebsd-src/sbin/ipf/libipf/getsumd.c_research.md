# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/getsumd.c

This helper formats a checksum delta/status value into a static string.

If `NAT_HW_CKSUM` is set, it formats `hw(<low16>)`; otherwise it formats the full value in hex. The returned pointer is to a static buffer overwritten on each call.
