# File Research: sources/os/plan9/9front/sys/src/9/port/ethersink.c

Implements a sink Ethernet driver: an Ethernet `/dev/null` useful as a bridge target for Ethernet-based VPNs. `reset` registers a non-linking 1000 Mbps pseudo-interface with attach, multicast, promiscuous, and control hooks.

`attach` makes the output queue nonblocking and sets its limit to zero, silently discarding output. The custom `ctl` accepts `ea <mac>` to set the interface MAC address. Multicast and promiscuous operations are no-ops.
