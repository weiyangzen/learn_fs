# File Research: sources/os/bsd/freebsd-src/sbin/ipf/common/pcap-ipf.h

## Purpose
Minimal pcap file header definitions used without including full libpcap/BPF headers.

## Main Elements
- Defines `pcaphdr_t` matching pcap file headers.
- Defines `TCPDUMP_MAGIC` and `PCAP_VERSION_MAJ`.
- Defines `pcappkt_t` for per-packet timestamp and lengths.

## Dependencies And Integration
Included by local BPF-related code that needs pcap structures without normal pcap headers.

## Risk Notes
This is a local structural copy; compatibility depends on staying aligned with pcap version 2 layout assumptions.
