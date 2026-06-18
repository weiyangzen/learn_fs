# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/af_inet.c

`af_inet.c` implements IPv4 address-family support for `ifconfig`. It registers the `inet` family, status printing, address parsing/copying, tunnel display/setup, CARP VHID plumbing, and add/delete execution through either legacy ioctls or netlink.

Status output prints the IPv4 address, point-to-point destination, netmask in configured format (`cidr`, `dotted`, or hex), broadcast address, and VHID. Address parsing accepts numeric addresses, host names, network names, and `addr/prefix` syntax; setting a new non-loopback/non-point-to-point address without a mask is rejected.

In ioctl builds it fills `in_aliasreq`/`ifreq` structures and uses `SIOCAIFADDR`/`SIOCDIFADDR`. In netlink builds it builds `RTM_NEWADDR`/`RTM_DELADDR` messages with `IFA_LOCAL`, optional destination/broadcast, FreeBSD flags, and VHID. It also emulates legacy `SIOCDIFADDR` behavior by deleting the first IPv4 address when no explicit delete address was supplied.
