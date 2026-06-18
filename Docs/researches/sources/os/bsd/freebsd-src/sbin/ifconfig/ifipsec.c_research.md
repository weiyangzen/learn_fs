# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/ifipsec.c

`ifipsec.c` adds ifconfig support for IPsec tunnel interfaces. It registers the `reqid` command and an `af_ipsec` status callback.

`ipsec_status()` fetches the current request ID with `IPSECGREQID` through `ioctl_ctx_ifr()` and prints `reqid: <value>` if available. `setreqid()` parses a numeric value with `strtoul()` and sends it using `IPSECSREQID`.

Dependencies are `net/if_ipsec.h`, standard ifreq ioctl plumbing, and the shared ifconfig registration interface.

Notable behavior: parse errors warn and return rather than exiting; ioctl set failures also warn and return. The parsed value is stored in `uint32_t`, but there is no explicit range or `ERANGE` validation beyond checking trailing characters.
