# File Research: sources/os/plan9/9front/sys/src/cmd/ip/measure.c

Ethernet traffic sampler for a target MAC address. It opens an Ethernet device in promiscuous mode, reads timestamped frames, recognizes IPv4/Ethernet variants, and accumulates inbound/outbound byte and packet counts by IP protocol.

At each sample interval it prints epoch time, elapsed capture time, and counters for all IP traffic plus selected multicast, UDP, and TCP protocols. Options enable debug output and limit the number of samples.
