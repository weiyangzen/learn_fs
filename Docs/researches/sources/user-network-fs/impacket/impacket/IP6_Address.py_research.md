# sources/user-network-fs/impacket/impacket/IP6_Address.py

Purpose: `IP6_Address.py` provides a lightweight IPv6 address parser, formatter, classifier, and byte representation for Impacket's IPv6 packet classes.

Important APIs, types, and functions: `IP6_Address(address)` accepts a text address or 16-byte sequence. Public projectors include `as_string(compress_address=True, scoped_address=True)`, `as_bytes()`, `get_scope_id()`, and `get_unscoped_address()`. Semantic helpers include `is_multicast()`, `is_unicast()`, `is_link_local_unicast()`, `is_site_local_unicast()`, `is_unique_local_unicast()`, and `get_human_readable_address_type()`. `is_a_valid_text_representation()` uses construction as validation. Private helpers parse scoped addresses, expand `::`, insert leading zeroes, and compress output by trimming leading zeroes and the longest zero chain.

Control flow: Construction initializes a 16-byte zero array and empty scope id, then dispatches to string or byte parsing. String parsing separates a single `%scope`, expands compressed notation if present, pads each group to four hex digits, validates total text length and group count, and fills the byte array two bytes at a time. Formatting emits full hex groups, optionally trims leading zeroes and the longest zero group chain, and appends scope if requested.

State and persistence behavior: State is the private byte array and optional scope id. There is no persistence. `as_bytes()` returns the underlying array object rather than a defensive copy, so callers can mutate address state.

Dependencies and integration points: The module depends on `array` and `six.string_types`. It is used by `IP6`, `ICMP6`, and code needing IPv6 address display or classification.

Risks: The unicast classifier treats only `0xFE...` addresses as unicast and returns `unknown type` for many ordinary global unicast addresses. The parser does not support IPv4-embedded dotted-decimal notation. `__from_bytes()` stores the provided object directly if length is 16, which can preserve mutability and non-array types. Compression of all-zero or edge zero chains should be regression-tested carefully.

Test signals: Tests should cover full and compressed text forms, scoped addresses, invalid triple/multiple compression markers, round-trip string/bytes behavior, longest-zero-chain compression, all-zero and loopback forms, scope omission, and address-type classification edge cases.
