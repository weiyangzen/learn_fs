# sources/user-network-fs/impacket/examples/sniff.py

## Purpose

`sniff.py` is a pcap-based live packet sniffer. It prompts for a capture interface when needed, applies an optional BPF filter, decodes Ethernet or Linux cooked frames with ImpactDecoder, and prints decoded packets.

## Important APIs, Types, and Functions

`DecoderThread` selects `EthDecoder` or `LinuxSLLDecoder` based on `pcapObj.datalink()`, then runs `pcap.loop(0, packetHandler)`. `packetHandler()` decodes and prints each packet. `getInterface()` lists devices from `pcapy.findalldevs()` and prompts if there are multiple. `main(filter)` opens the interface with `open_live()`, sets the BPF filter, prints capture metadata, and starts the decoder thread.

## Control Flow

The script treats all command-line arguments as one BPF filter string. It prints a deprecation warning banner, selects an interface, opens a live pcap handle with snaplen 1500, non-promiscuous mode, and 100 ms timeout, applies the filter, prints network/mask/linktype, and starts the background decoder thread.

## State and Persistence Behavior

It captures live network traffic and prints decoded packet structures. It writes no files. The process runs indefinitely until interrupted, and the background thread owns the pcap loop.

## Dependencies and Integration Points

It depends on `pcapy`, libpcap permissions/device availability, Impacket `ImpactDecoder`, and link-layer constants `DLT_EN10MB` and `DLT_LINUX_SLL`.

## Risks and Edge Cases

Live capture often requires elevated privileges. Unsupported datalink types raise an exception. Interface selection does not validate numeric input. The pcap handle is not explicitly closed. Packet printing can be very noisy and may expose sensitive traffic. The code starts a non-daemon thread and has no graceful stop path.

## Test Signals

Unit tests can mock pcap handles for datalink selection, filter application, interface selection branches, and packet decoding. Integration tests should verify BPF filters, Ethernet and Linux SLL captures, unsupported datalink behavior, and permission-denied messaging.
