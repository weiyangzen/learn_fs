# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/dhcpd/dat.h

`dat.h` is the DHCP server shared header.

Key contents:
- `Binding` tracks an IP lease: bound/offered client ids, lease/offer expiry, touch/complaint/probe timestamps, and qid of persisted lease file.
- `Info` holds NDB-derived host/network/server metadata: domain, boot files, TFTP, address/mask/net, Ethernet, gateway, fs/auth servers, rootpath, DHCP group, vendor data.
- Declares cross-file functions for lease database, NDB lookup, ICMP probing, logging, and globals.

Important dependencies:
- Includes `../dhcp.h`.
- Shared by server, helpers, and tests.

Notable risks/quirks:
- Mixes production declarations with test/helper-facing globals.
