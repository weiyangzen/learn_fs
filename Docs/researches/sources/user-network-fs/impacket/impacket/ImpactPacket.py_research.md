# sources/user-network-fs/impacket/impacket/ImpactPacket.py

## Purpose

`ImpactPacket.py` is Impacket's older low-level packet construction and parsing layer for common link, network, and transport headers. It provides mutable byte-buffer primitives, parent/child protocol composition, packet serialization, checksum helpers, and protocol-specific wrappers for Ethernet, Linux cooked capture, IPv4, IP options, UDP, TCP, TCP options, ICMP, IGMP, ARP, and raw payload data.

## Important APIs, Types, and Functions

The foundational types are `PacketBuffer`, `ProtocolLayer`, `ProtocolPacket`, and `Header`. `PacketBuffer` owns an `array.array('B')` and exposes typed byte, word, long, long-long, IP address, and checksum accessors. `ProtocolLayer` supplies the parent/child graph via `contains`, `set_parent`, `child`, `parent`, and `unlink_child`. `Header` combines packet bytes with protocol graph behavior and defines `get_packet`, `get_size`, `calculate_checksum`, `get_pseudo_header`, `load_header`, and printable hexdump formatting.

Concrete protocol classes include `Data`, `EthernetTag`, `Ethernet`, `LinuxSLL`, `IP`, `IPOption`, `UDP`, `TCP`, `TCPOption`, `ICMP`, `IGMP`, and `ARP`. The protocol classes export field-level getters/setters such as `IP.set_ip_src`, `IP.add_option`, `IP.fragment_by_size`, `UDP.set_uh_sport`, `TCP.set_SYN`, `TCP.add_option`, `ICMP.isPortUnreachable`, and ARP sender/target accessors. Module-level `array_tobytes` and `array_frombytes` smooth Python 2/3 `array` byte conversion differences.

## Control Flow

Packet construction is hierarchical. A parent header calls `contains(child)`, and `Header.get_packet()` recalculates checksums, serializes its own bytes, then appends `child.get_packet()` when present. `Ethernet.get_packet()` derives the EtherType from the child `ethertype`; `IP.get_packet()` derives protocol from the child `protocol`, fills total length when zero, appends IP options, pads the header to a 32-bit boundary, updates header length, and computes the IPv4 checksum when `auto_checksum` is enabled. `UDP` and `TCP` use the parent IP pseudo-header for transport checksums.

Parsing flows through `load_header` methods. `Ethernet.load_header()` counts stacked VLAN tags before setting header length. `IP.load_header()` uses the header-length nibble to parse options and raises `ImpactPacketException` on truncated or overlong option data. `TCP.load_header()` similarly parses options based on the data-offset nibble and validates option lengths. Fragment helpers copy the original IP header, split child payload into `Data` children, and set fragment offsets and MF flags.

## State and Persistence Behavior

All state is in memory. Buffers are mutable arrays that grow automatically when setters write beyond current length. Checksums are stateful through `auto_checksum`: explicit checksum setters usually disable later automatic recomputation, while reset helpers re-enable it. Packet hierarchy state is held by private parent/child references and can be broken by `load_body` or `load_packet`. IP and TCP options are held in private lists and serialized dynamically; they are not directly persisted to the base header bytes until packet emission.

## Dependencies and Integration Points

The module depends only on Python standard library modules (`array`, `struct`, `socket`, `string`, `sys`, `binascii`, `functools`) and integrates with other Impacket packet decoders through shared `Header`, `PacketBuffer`, `Data`, `ethertype`, and `protocol` conventions. `NDP.py`, `cdp.py`, and many packet examples build on these base classes. Callers that send raw packets rely on `get_packet()` returning wire-ready bytes.

## Risks and Edge Cases

The code is intentionally low-level and trusts many caller-provided lengths and values. `PacketBuffer.__validate_index` auto-expands buffers, which is convenient for construction but can mask malformed offsets. `IP.fragment_by_list()` rounds requested fragment sizes up to multiples of eight and has a remaining-data path that sets the raw offset value inconsistently with earlier fragments. IP and TCP option parsing protects against truncated and invalid lengths, but many other field getters assume enough bytes are present. Transport checksum computation depends on a correct parent pseudo-header and can silently skip UDP checksum work when there is no parent. Several methods use broad exception handling or legacy string/byte assumptions.

## Test Signals

Useful tests include byte-for-byte serialization of Ethernet/VLAN/IP/UDP/TCP/ICMP/ARP packets, checksum verification with and without explicit checksum overrides, IPv4 and TCP option round-trips including EOL/NOP/truncated options, VLAN push/pop behavior, BSD byte-order handling for IPv4 length/offset fields, and IP fragmentation offset/MF behavior. Integration tests should build nested packet trees and compare output with pcap fixtures or known wire encodings.
