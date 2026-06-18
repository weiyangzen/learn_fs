# File Research: sources/os/bsd/freebsd-src/sbin/dhclient/dhcp.h

## Purpose
Defines DHCP/BOOTP wire-format constants, packet layout, option codes, and DHCP message type identifiers.

## Main Elements
- Size constants: Ethernet/IP/UDP overhead, BOOTP/DHCP fixed lengths, MTU and option buffer lengths.
- `struct dhcp_packet`: on-wire BOOTP/DHCP message fields including `op`, `htype`, `hlen`, transaction ID, addresses, hardware address, `sname`, `file`, and `options`.
- BOOTP constants: `BOOTREQUEST`, `BOOTREPLY`, broadcast flag, hardware types.
- DHCP magic cookie: `DHCP_OPTIONS_COOKIE`.
- DHCP option code macros for common RFC options, DHCP control options, domain search, classless routes, vendor options, and end marker.
- DHCP message type macros: `DHCPDISCOVER`, `DHCPOFFER`, `DHCPREQUEST`, `DHCPDECLINE`, `DHCPACK`, `DHCPNAK`, `DHCPRELEASE`, `DHCPINFORM`.

## Dependencies And Integration
Included by `dhcpd.h`, which is then included across dhclient source files. Option code constants index `dhcp_options[256]`, packet option arrays, parser tokens, and script export logic.

## Risk Notes
These constants must match protocol wire values. Incorrect sizes or option codes would corrupt packet parsing, option assembly, lease validation, and script environment generation.
