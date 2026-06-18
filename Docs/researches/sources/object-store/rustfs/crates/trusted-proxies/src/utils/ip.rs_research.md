# sources/object-store/rustfs/crates/trusted-proxies/src/utils/ip.rs

Purpose: IP classification, parsing, range membership, and canonicalization helpers.

Important APIs: `IpUtils` methods for valid/reserved/private/loopback/link-local/documentation classification; `parse_ip_or_cidr`, `parse_ip_list`, `parse_network_list`, `ip_in_networks`, `get_ip_type`, `canonical_ip`; free `is_valid_ip_address`.

Control flow: Classification uses std `IpAddr` methods plus explicit octet/segment pattern matches. Parsing splits comma lists, trims empty entries, and returns errors on invalid non-empty tokens. `get_ip_type` orders checks as private, loopback, link-local, documentation, reserved, public.

State and dependencies: Stateless; depends on `ipnetwork` and std net types.

Integration points: `ProxyChainAnalyzer` uses the free `is_valid_ip_address`; tests import `IpUtils` through crate root.

Risks and tests: `is_valid_ip_address` allows documentation/reserved/private addresses, intentionally separating syntax/usefulness from policy. Reserved IPv4 matching includes private and multicast ranges, while `get_ip_type` masks private before reserved. Unit IP tests cover all classifications, parsing, network membership, type ordering, and canonical formatting.
