# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/dhcp.h

`dhcp.h` defines DHCP/BOOTP protocol constants and the packet structure shared by client/server tools.

Key contents:
- Lease/time constants, DHCP states, BOOTP operation values, flags, and option numbers.
- Includes standard BOOTP options, DHCP options, PXE options, deprecated Plan 9 v4 vendor options, and textual Plan 9 vendor options.
- `Bootp` embeds a Plan 9 UDP header, fixed BOOTP fields, magic cookie, and option data.
- Defines `Lforever` as an infinite lease marker.

Important dependencies:
- Used by `dhcpclient.c` and `dhcpd` sources.

Notable risks/quirks:
- `Maxoptlen` is fixed to `312-4`.
- Plan 9 vendor options are integrated directly into the shared protocol enum.
