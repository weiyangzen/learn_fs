# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/ipft_pc.c

Classic pcap packet-input backend for IPFilter test tooling.

Key behavior:
- Exports `pcap` as an `ipread` provider.
- Reads the pcap file header, detects byte-swapped captures, and supports a small set of DLT/link types.
- Reads packet records, strips configured link-layer header/type bytes, and returns packet payload into `mb_t`.

Research notes:
- Only a few link-layer types are understood.
- Allocated static packet buffer is resized but not freed by this module.
- The IP protocol type bytes are copied into `ty` but the filtering loop is disabled.
