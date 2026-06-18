# File Research: sources/os/bsd/netbsd-src/lib/libc/net/getifaddrs.c

Read completely: 306 lines.

This file implements `getifaddrs` and `freeifaddrs`. It retrieves interface/address data through `sysctl` over `NET_RT_IFLIST`, counts required `ifaddrs`, sockaddr, interface-data, and name storage, then allocates one combined block containing the linked list and all referenced data.

The first pass sizes interface info and address records; the second pass fills `struct ifaddrs` entries for `RTM_IFINFO` and `RTM_NEWADDR`, including link-layer addresses, netmasks, broadcast addresses, flags, address flags, interface names, and aligned `if_data`.

Security/reliability notes: the implementation assumes route-message lengths from the kernel are trustworthy enough for iteration. `freeifaddrs` frees the single allocation; callers must not free nested pointers independently.
