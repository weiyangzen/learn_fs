# File Research: sources/os/bsd/freebsd-src/sbin/devd/dhclient.conf

## Purpose
Starts `dhclient` when DHCP-capable network links come up.

## Main Elements
- IFNET `LINK_UP` with Ethernet media starts `service dhclient quietstart $subsystem`.
- IFNET `LINK_UP` with 802.11 media does the same.
- No link-down rule; comments state `dhclient` exits automatically on link down.

## Dependencies And Integration
Uses `media-type` match support implemented in `devd.cc`.
