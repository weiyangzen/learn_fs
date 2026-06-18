# File Research: sources/os/bsd/freebsd-src/sys/kern/uipc_mbufhash.c

## Summary
Computes FNV-based packet hashes over selected L2, L3, and L4 fields for Ethernet and InfiniBand mbufs.

## Main Responsibilities
- Initializes per-consumer hash seeds for Ethernet and InfiniBand TCP/IP hashing.
- Safely reads headers from potentially non-contiguous mbuf chains.
- Hashes Ethernet source/destination addresses and VLAN tags when requested.
- Hashes InfiniBand hardware addresses when requested.
- Hashes IPv4/IPv6 addresses, IPv4 transport ports, and IPv6 flow labels according to flags.

## Key APIs
- `m_ether_tcpip_hash_init()`, `m_infiniband_tcpip_hash_init()`.
- `m_ether_tcpip_hash()`, `m_infiniband_tcpip_hash()`.

## Important Behavior
`m_common_hash_gethdr()` returns a direct pointer when the requested header is contiguous in the first mbuf; otherwise it copies the header into a caller-supplied stack buffer. It rejects reads beyond `m_pkthdr.len`.

For Ethernet, `m_ether_tcpip_hash()` starts after the Ethernet header, optionally hashes L2 addresses, handles hardware VLAN tags from `M_VLANTAG`, and parses in-frame VLAN headers before dispatching to IP hashing.

For IPv4, L3 hashing covers source/destination addresses. L4 hashing covers the first four bytes of TCP, UDP, or SCTP headers after validating the IPv4 header length. For IPv6, L3 hashing covers source/destination addresses and L4 hashing uses the flow label rather than walking extension headers.

InfiniBand hashing reads `ib_protocol`, optionally hashes the hardware address, and then reuses the same TCP/IP hash helper.

## State and Synchronization
The functions are pure readers of the mbuf chain and return an updated hash accumulator. Seed initialization uses `arc4random()` and FNV over the random seed.

## Risks
The parser is intentionally shallow. IPv6 L4 hashing does not inspect transport ports, and IPv4 options or fragmented/truncated packets can limit L4 contribution. Callers must choose hash flags that match their load-balancing semantics.
