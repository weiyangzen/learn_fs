# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/ether/dat.h

This header defines shared data structures and globals for USB Ethernet drivers. `Block` is the packet buffer with read/write pointers, limit, base storage, and next pointer; `BLEN`, `allocb`, `copyblock`, and `freeb` provide lightweight buffer operations.

It defines Ethernet constants (`Eaddrlen`, `ETHERHDRSIZE`, `Maxpkt`), `Etherpkt` header layout, CDC descriptor constants used during endpoint/interface discovery, and `Macent` entries for the bridge-learning table.

The globals include debug flags, user-specified MAC flag, promiscuous/multicast counters, multicast address table, active MAC address, bridge MAC table, `etheriq()` ingress hook, and driver callback slots. Chip-specific files fill `epreceive`, `eptransmit`, and optional promiscuous/multicast/link-speed callbacks during initialization.
