# sources/object-store/rustfs/crates/trusted-proxies/tests/unit/ip_tests.rs

Purpose: Unit tests for `IpUtils` parsing, classification, membership, and canonicalization.

Important APIs tested: `is_valid_ip_address`, reserved/private/loopback/link-local/documentation classifiers, `parse_ip_or_cidr`, `parse_ip_list`, `parse_network_list`, `ip_in_networks`, `get_ip_type`, and `canonical_ip`.

Control flow: Tests construct representative IPv4/IPv6 addresses, verify positive and negative classification boundaries, ensure parse failures propagate on invalid list entries, and compare canonical strings or re-parsed IPv6 equality where formatting can vary.

State and dependencies: Pure tests with no global state. Uses std `IpAddr` parsing and public crate exports.

Integration points: Provides confidence for chain validation's `is_valid_ip_address` assumptions and public utility behavior.

Risks and coverage gaps: Does not exhaust all special-use IP ranges. Tests document that reserved and valid are separate concepts: documentation IPv6 is still valid for general use.
