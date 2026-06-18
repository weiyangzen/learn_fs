
# sources/security-integrity/keyutils/dns.afsdb.c

## Purpose
`dns.afsdb.c` extends `key.dns_resolver` with AFS volume-location DNS support. It resolves AFSDB or RFC 5864 SRV records for a cell into address payloads that can instantiate a kernel `dns_resolver` key for kAFS.

## Important APIs, Types, And Functions
`afsdb_hosts_to_addrs()` parses AFSDB records, deduplicates VL server names, resolves them with `dns_resolver()`, and tracks minimum TTL. `srv_hosts_to_addrs()` does the same for `_afs3-vlserver._udp.<cell>` SRV records, adding `+port` suffixes. `dns_query_AFSDB()` and `dns_query_VL_SRV()` issue resolver queries and parse DNS responses. `afs_instantiate()` sets key timeout, appends a terminating NUL payload segment, dumps payload, and calls `keyctl_instantiate_iov()`. `afs_look_up_VL_servers()` selects address-family mask options, tries SRV first, falls back to AFSDB, and instantiates.

## Control Flow
The public entry point is `afs_look_up_VL_servers(cell, options)`. It constrains `mask` for `ipv4` or `ipv6`, queries SRV records first, falls back to AFSDB on failure, then calls the no-return instantiation path. Record parsing walks answer sections, expands compressed target names, ignores duplicates, resolves targets to addresses, and records the minimum TTL.

## State And Persistence
The file modifies globals from `key.dns_resolver.c`: `mask`, `payload`, `payload_index`, `key_expiry`, `key`, and `debug_mode`. In non-debug mode it sets kernel key timeout and instantiates the key payload.

## Dependencies And Integration Points
It depends on libresolv nameser APIs, `getaddrinfo()` through shared `dns_resolver()`, and keyutils key instantiation. It is compiled into `key.dns_resolver` by the Makefile.

## Risks
`vllist` is capped by `MAX_VLS` but the code does not explicitly stop before exceeding the array if DNS returns many unique records. Some allocated host strings are not freed after successful use because the process exits soon after instantiation. `strcmp(options, ...)` assumes non-null options from the caller.

## Test Signals
Testing requires debug-mode invocations or request-key integration with controlled DNS records. Useful signals are payload contents, TTL selection, duplicate suppression, SRV fallback to AFSDB, and IPv4/IPv6 option handling.
