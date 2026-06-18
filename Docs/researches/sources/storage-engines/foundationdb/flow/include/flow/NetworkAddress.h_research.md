<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/NetworkAddress.h -->
# sources/storage-engines/foundationdb/flow/include/flow/NetworkAddress.h

Purpose: This header defines Flow's canonical network endpoint value types. `NetworkAddress` represents one TCP endpoint with an `IPAddress`, port, privacy/TLS flags, and a hostname-origin marker; `NetworkAddressList` pairs a primary address with an optional secondary address; `AddressExclusion` models process or whole-machine exclusions.

Important APIs and types: Key APIs are the overloaded `NetworkAddress` constructors, comparison operators, `isValid`, `isPublic`, `isTLS`, `isV6`, `hash`, `parse`, `parseOptional`, `parseList`, `toString`, and serialization. `NetworkAddressList::getTLSAddress`, `contains`, and `toString` capture dual-address behavior. `AddressExclusion::parse`, `excludes`, and `isWholeMachine` support exclusion rules. The file also specializes `Traceable<NetworkAddress>` and `std::hash<NetworkAddress>`.

Control flow: Construction encodes public/private and TLS state into bit flags. Serialization is protocol-version-aware: old protocol versions without IPv6 read and write a legacy IPv4 integer, and newer versions can include the `fromHostname` flag. `NetworkAddressList::getTLSAddress` selects the primary address when there is no secondary or the primary is already TLS, otherwise returns the secondary.

State and persistence behavior: The address structures are value objects with no internal persistence, but they are serialized into cluster, worker, and trace-facing messages. Equality and ordering intentionally ignore `fromHostname`, because `operator==` compares only `ip`, `port`, and `flags`; this is important if hostname provenance is diagnostic rather than identity state. `AddressExclusion::toString` is explicitly marked debugging-only and should not be used as durable serialization.

Dependencies and integration points: The header depends on `IPAddress`, `Optional`, `BooleanParam`, `Trace`, and Flow's serializer traits. It is used by networking, TLS policy, trace local address state, system monitor identity, address exclusion commands, and metric key generation through address strings.

Risks: The IPv6 hash only uses the trailing 48 bits plus port, so hash collisions are possible for broad IPv6 sets. Protocol-gated serialization must remain compatible with mixed-version clusters. Identity operations omitting `fromHostname` can surprise code that expects hostname-derived addresses to compare distinctly.

Test signals: Useful tests include round-trip parsing and `toString` for IPv4, IPv6, TLS, and private/public forms; mixed-protocol serialization for pre-IPv6 and hostname-flag versions; `NetworkAddressList::getTLSAddress`; exclusion matching for whole-machine and single-port rules; ordering and hash consistency in maps.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/NetworkAddress.h -->
