# File Research: sources/os/plan9/9front/sys/src/cmd/ip/hogports.c

Utility that reserves port ranges by announcing each requested address and then sleeping forever. Arguments are `proto!start-end` style ranges.

The process forks into the background, closes standard fds, announces all ports, closes stderr, and keeps the namespace alive. Useful for preventing other services from binding selected ports.
