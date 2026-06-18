# File Research: sources/os/plan9/9front/sys/src/cmd/ip/dhcpd/ndb.c

Ndb integration for the IPv4 DHCP server. Opens/reopens the ndb file on change, finds interfaces, derives local reply addresses, and looks up host/network metadata by IP and hardware address.

`lookupip` fills `Info` with address, mask, gateway, domain, boot files, TFTP, fs/auth, NFS root, and vendor attributes. `lookup` maps a BOOTP client to an `Info` record using `ciaddr` or Ethernet address constrained to the requester/relay network.

Also provides helpers for server-address lists and domain names used by DHCP option generation.
