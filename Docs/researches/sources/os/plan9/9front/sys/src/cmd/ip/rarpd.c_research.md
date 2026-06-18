# File Research: sources/os/plan9/9front/sys/src/cmd/ip/rarpd.c

This is a RARP daemon. It listens for Ethernet type `0x8035`, looks up client Ethernet addresses in NDB, replies with IPv4 addresses, and optionally populates the local ARP table.

`main` parses Ethernet device, net mount point, NDB file, and debug options. It opens the NDB database, dials the RARP Ethernet endpoint, gets the server’s local IP and Ethernet address, opens `/net/arp` if available, forks into the background, and loops reading RARP packets.

For each valid request, it checks packet size and operation, formats the target hardware address, looks up `ether=<addr>` to `ip=<addr>` with `lookup`, fills target protocol address, sets sender hardware/protocol fields to the server, changes op to RARP reply, and sends a minimum Ethernet frame.

`lookup` wraps `ndbipinfo`, defaulting source attribute via `ipattr` when needed. The daemon logs failures through syslog with log name `ipboot`.
