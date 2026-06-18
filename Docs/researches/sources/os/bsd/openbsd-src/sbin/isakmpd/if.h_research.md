# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/if.h

Declares `if_map(int (*)(char *, struct sockaddr *, void *), void *)`.

The header includes `sys/types.h`, forward-declares `struct ifreq`, and leaves address-family-specific handling to callback users.
