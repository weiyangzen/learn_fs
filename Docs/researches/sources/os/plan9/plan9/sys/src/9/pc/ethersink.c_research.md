# File Research: sources/os/plan9/plan9/sys/src/9/pc/ethersink.c

Minimal synthetic Ethernet sink driver, described as an Ethernet `/dev/null` useful as a bridging target for Ethernet-based VPNs. It registers as `"sink"` through `ethersinklink()`.

`reset()` only accepts devices with a non-nil type, sets link speed to 1000 Mbps, installs no-op attach/transmit callbacks, disables IRQ and interrupt handling, clears stat/promiscuous/multicast hooks, installs a custom control hook, and uses the `Ether` itself as `arg`. It does not allocate hardware or buffers.

`ctl()` supports one command: `ea <ether-address>`. It parses the command, validates the address with `parseether`, and updates both `ether->ea` and `ether->addr`. Any other command raises `Ebadctl`. `nop()` is used for attach/transmit.

The file intentionally drops all transmitted packets and never receives packets. Its only mutable behavior is setting the visible Ethernet address.
