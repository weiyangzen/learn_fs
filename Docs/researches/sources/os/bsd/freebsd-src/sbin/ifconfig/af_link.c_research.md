# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/af_link.c

`af_link.c` implements link-layer address handling for the `link`, `ether`, and `lladdr` address families. It registers three names that share the same status, parser, and `SIOCSIFLLADDR` execution path.

Status printing emits Ethernet addresses in the selected format (`colon`, `dash`, or `dotted`) or generic `lladdr` text from `link_ntoa()`. It also prints original hardware address when available and meaningfully different, and prints LAN PCP if configured.

Address setting accepts `random`, generating a locally administered non-multicast Ethernet address, or parses a supplied link address with `link_addr()`. It rejects attempts to set link-level netmask or broadcast values.
