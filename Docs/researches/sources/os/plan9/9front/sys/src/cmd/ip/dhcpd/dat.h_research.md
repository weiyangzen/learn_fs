# File Research: sources/os/plan9/9front/sys/src/cmd/ip/dhcpd/dat.h

Internal header for the IPv4 DHCP server. Defines `Binding` for file-backed lease state and `Info` for ndb-derived host/network metadata including IP, mask, gateway, boot files, TFTP, fs/auth, root server/path, and vendor text.

Declares cross-file functions from `db.c`, `ndb.c`, and ICMP probing, plus globals such as `binddir`, `blog`, `now`, `ndbfile`, and lease policy values.
