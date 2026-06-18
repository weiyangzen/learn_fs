# sources/user-network-fs/impacket/impacket/pcap_linktypes.py

## Purpose
`pcap_linktypes.py` is a constant table for libpcap link-layer type identifiers. It exposes both `LINKTYPE_*` names and common `DLT_*` aliases so packet capture readers and writers can specify or inspect the `linkType` field in classic pcap file headers without depending on an external pcap binding.

## Important APIs, Types, and Functions
The file defines constants only; it has no functions or classes. The most common entries are `LINKTYPE_NULL`/`DLT_NULL`, `LINKTYPE_ETHERNET`/`DLT_EN10MB`, `LINKTYPE_RAW`/`DLT_RAW`, `LINKTYPE_IEEE802_11`, `LINKTYPE_IEEE802_11_RADIOTAP`, `LINKTYPE_LINUX_SLL`, `LINKTYPE_IPV4`, and `LINKTYPE_IPV6`. Many less common capture formats are also mapped, including PPP, FDDI, Bluetooth, USB, CAN SocketCAN, DBus, NFLOG, Infiniband, SCTP, PKTAP, EPON, and IPMI HPM.2.

## Control Flow
There is no runtime control flow beyond module import. Importing the module binds numeric constants into the module namespace for direct use by pcap writers, pcap readers, decoders, tests, or callers selecting capture encapsulation.

## State and Persistence Behavior
State is static module-level integer bindings. No mutable structures, files, sockets, or persistent side effects are created.

## Dependencies and Integration Points
The module has no imports. Its primary local integration point is `pcapfile.py`, whose pcap header has a default `linkType` of Ethernet and exposes `setLinkType()`/`getLinkType()`. Broader Impacket capture or decoder code can use these constants to align pcap headers with packet decoder expectations.

## Risks and Edge Cases
The constant `NKTYPE_IEEE802_5` appears to be a misspelled `LINKTYPE_IEEE802_5`, and `DLT_IEEE802` aliases that misspelled name. Code expecting the canonical `LINKTYPE_IEEE802_5` symbol will not find it. The table is static and may lag newer tcpdump.org assignments. There is no reverse lookup, validation, or duplicate detection, so callers must know whether a value is appropriate for the payload bytes they write.

## Test Signals
Tests should assert representative alias equality, especially Ethernet, raw IPv4/IPv6, radiotap, Linux cooked capture, and USB/Bluetooth names used by callers. A smoke import test should catch syntax or accidental rename regressions. If consumers depend on Token Ring naming, add a test documenting the current `NKTYPE_IEEE802_5` spelling or introducing a compatibility alias deliberately.
