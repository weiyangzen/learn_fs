# File Research: sources/os/plan9/plan9/sys/src/9/boot/bootip.c

Boot-time IP configuration and TCP root connection support.

Key behavior:
- `configip()` binds IP and Ethernet interfaces into `/net` or `/netX`, runs `/boot/ipconfig`, waits for DHCP/config completion, and optionally prompts for filesystem/auth IPs.
- Reads filesystem/auth server IPs from network `ndb`, environment, or interactive prompt.
- `configtcp()` configures IP and sets `authaddr` to TCP port 567 for auth.
- `connecttcp()` dials filesystem server at TCP port 564.
- Handles `-x` net mount point and ignores several ipconfig options while parsing.

This supports network boot from a TCP 9P file server.
