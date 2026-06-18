# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/sockraw.c

This is a raw IPv4 socket output backend.

`initdevice()` opens `socket(AF_INET, SOCK_RAW, IPPROTO_RAW)`, obtains the interface address with `SIOCGIFADDR`, and binds the raw socket.

`sendip()` strips the Ethernet header from the supplied frame, derives the destination IPv4 address from the IP header, and sends the IP packet with `sendto()`.

The file warns that attempting to use it on HP-UX 11.00 can crash the system.

Implementation notes and risks:
- Despite accepting Ethernet-framed input, it transmits only the IP portion.
- Interface bind code copies `ifr.ifr_addr` into `sa_data` in a legacy style.
- Intended as a platform fallback, not a portable primary backend.
