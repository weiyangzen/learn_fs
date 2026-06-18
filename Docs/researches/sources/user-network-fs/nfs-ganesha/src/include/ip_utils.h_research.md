# sources/user-network-fs/nfs-ganesha/src/include/ip_utils.h

## Purpose

`ip_utils.h` centralizes socket address and CIDR utilities used by export/client matching, duplicate request cache keys, logging, and network identity handling. It covers IPv4, IPv6, optional VSOCK, loopback/any checks, display formatting, hashing, and IPv4-mapped IPv6 normalization.

## Important APIs, Types, and Functions

`sockaddr_t` aliases `sockaddr_storage`; `CIDR` stores an address and mask. CIDR APIs allocate, duplicate, parse from string, render to string, compare, normalize v4-mapped addresses, compute family/protocol/version, and test containment. Socket APIs include `sockaddr_cmp`, `hash_sockaddr`, `ip_str_to_sockaddr`, `get_port`, `get_sockport`, address conversion helpers, `is_loopback`, `is_inaddrany`, and display helpers. Inline `socket_addr`, `socket_addr_len`, and `sprint_sockip` abstract per-family payload access.

## Control Flow

Callers parse configuration or client identities into `sockaddr_t`/`CIDR`, normalize comparable forms, hash or compare addresses with optional port inclusion, and format addresses for logs or metrics. Export client matching can use CIDR containment and HA/proxy-aware address selection upstream.

## State and Persistence Behavior

The utilities are stateless except for allocated `CIDR` and string results owned by callers. Network identities may become persistent only when other subsystems store parsed addresses in caches or export/client entries.

## Dependencies and Integration Points

The header depends on libc networking headers, byte-order helpers, `display.h`, and optional RPC VSOCK definitions. It integrates with `log.h`, `nfs_dupreq.h`, client/export managers, IP-name cache, and conditional logging.

## Risks and Test Signals

Risks include inconsistent IPv4-mapped IPv6 normalization, comparing ports when callers expect host-only identity, VSOCK length/hash mistakes, buffer truncation in `sprint_sockip`, and ownership leaks from `cidr_to_str`. Tests should cover IPv4/IPv6/v4-mapped parsing, CIDR edge masks, port-sensitive and port-insensitive compare/hash, AF_LOCAL/VSOCK branches when enabled, display buffer truncation, and invalid input rejection.
