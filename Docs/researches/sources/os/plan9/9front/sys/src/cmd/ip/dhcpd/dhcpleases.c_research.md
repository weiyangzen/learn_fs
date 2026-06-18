# File Research: sources/os/plan9/9front/sys/src/cmd/ip/dhcpd/dhcpleases.c

Small lease-reporting utility. It scans `binddir`, parses filenames as IP addresses, synchronizes each binding through `syncbinding`, and prints active leases with bound client ID and expiration time.

Uses the same binding structures and validation logic as `dhcpd`, making it a read-side view over the DHCP lease directory.
