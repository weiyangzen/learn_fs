# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/hogports.c

Small daemon that reserves TCP/UDP-style port ranges by announcing each specified `proto!start-end` address. It forks into the background, closes standard descriptors, announces every port, and sleeps forever so other services cannot bind those ports.
