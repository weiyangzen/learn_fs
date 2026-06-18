# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/checkrev.c

This helper checks that the userland IPFilter version matches the kernel module/device version.

`checkrev()` opens the given IPFilter device once, builds an `ipfobj_t` for `IPFOBJ_IPFSTAT`, issues `SIOCGETFS`, and compares `IPL_VERSION` to the returned `friostat.f_version`.

On ioctl failure it reports through `ipferror()`, closes the cached descriptor, and returns `-1`; on mismatch it also returns `-1`.
