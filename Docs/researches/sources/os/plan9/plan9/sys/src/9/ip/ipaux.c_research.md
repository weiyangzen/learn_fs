# File Research: sources/os/plan9/plan9/sys/src/9/ip/ipaux.c

Provides shared IP utility data and helpers.

Key responsibilities:
- Defines IPv6 header type names and well-known IPv6 addresses/masks: unspecified, loopback, link-local, multicast, all-nodes/all-routers node/link scopes, solicited-node multicast.
- `ptclcsum` computes protocol checksums across block chains, handling odd byte alignment and multi-block carry folding.
- `ipv62smcast` maps an IPv6 address to its solicited-node multicast address.
- `parsemac` parses colon-separated hex MAC addresses.
- Implements connection hash helpers: `iphash`, `iphtadd`, `iphtrem`, and `iphtlook`.
- `iphtlook` applies precedence for exact connected 4-tuple, announced local address+port, port-only, address-only, and wildcard matches.

Notable design:
- The hash table stores match class at insertion time based on how specific a conversation’s local/remote tuple is.
