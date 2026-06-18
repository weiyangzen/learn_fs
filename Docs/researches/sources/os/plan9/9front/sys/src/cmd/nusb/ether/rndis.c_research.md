# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/ether/rndis.c

This file implements minimal RNDIS Ethernet support. It defines static RNDIS initialize, query-permanent-address, and set-current-filter messages, plus helpers to send and receive encapsulated control messages over class/interface control requests.

`rndisin()` repeatedly fetches control responses, rejects nonzero status, ignores asynchronous status messages, and reports short responses. `rndisinit()` sends the initialize message, validates the initialize-complete response, requires a connectionless 802.3 device, queries the permanent MAC address, validates returned offset/size, copies it to `macaddr`, sets a packet filter for all multicast plus broadcast, and installs callbacks.

Data transfer uses the RNDIS packet message header. `rndisreceive()` reads a USB packet, validates message type, total length, data offset, data length, and minimum Ethernet header size, then advances the block read pointer to the embedded Ethernet frame before calling `etheriq()`. `rndistransmit()` prepends a 44-byte RNDIS packet header around each Ethernet frame before writing to the endpoint.
