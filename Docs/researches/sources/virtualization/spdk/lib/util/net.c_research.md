# File Research: sources/virtualization/spdk/lib/util/net.c

This file implements small network address helpers.

`spdk_net_get_interface_name()` scans `getifaddrs()` for an up IPv4 interface whose address string matches the supplied IP, then copies the interface name. It returns `-ENODEV` if none match and `-ENOMEM` if the name does not fit.

`spdk_net_get_address_string()` converts `AF_INET` or `AF_INET6` sockaddr addresses to text through `inet_ntop()`. Unsupported families or `inet_ntop()` failures return negative errno.

`spdk_net_is_loopback()` gets the local socket address, finds the matching active interface, queries `SIOCGIFFLAGS`, and returns whether `IFF_LOOPBACK` is set. Failures return false.

`spdk_net_getaddr()` fills optional local address/port and peer address/port for a socket. It accepts Unix sockets as addressless, rejects unsupported families, rejects peer requests on listening sockets, and uses `getsockname()`, `getsockopt(SO_ACCEPTCONN)`, and `getpeername()` for TCP-style sockets.

`spdk_net_compare_address()` parses two IPv4 or IPv6 strings with `inet_pton()` and returns `memcmp()` ordering through `cmp`. It validates null arguments and address family, returning `-EAFNOSUPPORT` for unsupported families.

Important behavior is that several helpers log but return generic negative errno, and `spdk_net_is_loopback()` intentionally collapses all errors to false.
