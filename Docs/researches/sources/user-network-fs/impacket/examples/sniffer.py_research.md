# sources/user-network-fs/impacket/examples/sniffer.py

## Purpose

`sniffer.py` is a raw-socket IP packet sniffer. It listens for one or more IP protocols, decodes received packets with `ImpactDecoder.IPDecoder`, and prints them.

## Important APIs, Types, and Functions

There are no custom functions or classes. Module-level code computes `toListen`, creates one raw `AF_INET` socket per protocol from `socket.getprotobyname()`, sets `IP_HDRINCL`, uses `select()` to wait for packets, calls `recvfrom()`, and decodes with `ImpactDecoder.IPDecoder()`.

## Control Flow

With no arguments it listens for `icmp`, `tcp`, and `udp`. With arguments it treats each argument as a protocol name, skips unknown protocols, exits if none remain, then enters a loop over sockets ready for reading. Empty reads close and remove a socket; non-empty reads are decoded and printed.

## State and Persistence Behavior

The script opens raw sockets and prints live packet data. It writes no files and persists no state beyond the running process.

## Dependencies and Integration Points

It depends on OS raw socket support, protocol name resolution, `select`, and Impacket `ImpactDecoder`. It is IP-layer only and assumes returned packets include IP headers.

## Risks and Edge Cases

Raw sockets require elevated privileges on most systems and are platform-dependent. The code mutates `toListen` while iterating over it when dropping unknown protocols, which can skip later entries. There is no timeout or signal cleanup. Printed packet data may expose sensitive traffic.

## Test Signals

Mock tests should cover default protocols, unknown protocol filtering, empty protocol exit, socket creation options, empty reads, and decode/print flow. Integration tests require a privileged environment and controlled ICMP/TCP/UDP traffic.
