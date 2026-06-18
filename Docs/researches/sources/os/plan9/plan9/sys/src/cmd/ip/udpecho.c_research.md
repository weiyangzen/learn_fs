# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/udpecho.c

## Purpose
Simple UDP echo service.

## Behavior
Accepts `-x netmtpt`, announces `udp!*!echo`, enables `headers` mode on the control file, opens the announced conversation’s `data` file, then loops reading packets and writing the same bytes back.

## Dependencies
Uses Plan 9 `/net` UDP announce/open/read/write flow and `setnetmtpt`.
