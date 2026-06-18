# File Research: sources/virtualization/qemu/tools/ebpf/rss.bpf.c

## Purpose
eBPF socket filter program for virtio-net RSS steering. It parses packet headers, computes a Toeplitz RSS hash using QEMU-provided BPF maps, and returns a selected queue.

## Main Data Structures
- `rss_config_t`: runtime RSS configuration: redirect flag, hash population flag, hash types, indirection length, and default queue.
- `toeplitz_key_data_t`: preprocessed Toeplitz key state.
- `packet_hash_info_t`: parsed packet metadata for IPv4/IPv6, TCP/UDP, ports, fragmentation, and IPv6 extension source/destination addresses.
- BPF maps:
  - `tap_rss_map_configurations`
  - `tap_rss_map_toeplitz_key`
  - `tap_rss_map_indirection_table`

## Behavior
- `parse_eth_type()` handles Ethernet type parsing with single/double VLAN tags.
- `parse_packet()` extracts IPv4 or IPv6 addressing, detects fragmentation, and extracts TCP/UDP ports when safe.
- `parse_ipv6_ext()` walks bounded IPv6 extension headers, including routing header type 2 and home address destination option handling.
- `calculate_rss_hash()` builds an RSS input buffer based on negotiated virtio-net hash type bits and computes the Toeplitz hash.
- `tun_rss_steering_prog()` looks up config/key maps, computes hash if redirect is enabled, indexes the indirection table, and returns either selected queue or default queue.

## Safety/Verifier Constraints
- IPv6 extension and option parsing loops are bounded by `IP6_EXTENSIONS_COUNT` and `IP6_OPTIONS_COUNT`.
- Packet reads use `bpf_skb_load_bytes_relative()`.
- Hash input buffer is fixed-size and zero-initialized.
- Missing BPF map entries fall back to queue `0` or configured default queue.

## Filesystem/Storage Relevance
Indirect. This is virtualization networking support, not filesystem code, but it belongs to the QEMU virtualization source tree in subset A. It supports virtio-net multiqueue packet steering.

## Notable Detail
`net_toeplitz_add()` accepts a `len` argument but loops over `HASH_CALCULATION_BUFFER_SIZE`; the caller zero-fills the full buffer, so unused bytes contribute zero input.
