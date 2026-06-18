# sources/user-network-fs/impacket/impacket/ICMP6.py

Purpose: `ICMP6.py` defines an `ImpactPacket.Header` subclass for ICMPv6 packet construction, parsing, checksum calculation, message metadata, and helpers for common ICMPv6 message bodies.

Important APIs, types, and functions: `ICMP6` declares protocol number 58, header size 4, message type/code constants, node-information constants, and the `icmp_messages` description table. Accessors include `get_type()`, `get_code()`, `get_checksum()`, setters for the same fields, `calculate_checksum()`, `is_informational_message()`, `is_error_message()`, and `is_well_formed()`. Class factories build echo request/reply, destination unreachable, packet-too-big, time-exceeded, parameter-problem, neighbor solicitation/advertisement, and node information messages. Payload helpers expose target address, neighbor flags, node information qtype/nonce/flags/data, echo fields, MTU, parameter-problem pointer, and originating packet data.

Control flow: Construction creates a 4-byte header and optionally loads bytes. Message factories build the ICMP header, pack the message-specific body with `struct` and `array`, wrap it in `ImpactPacket.Data`, and link it with `contains()`. `calculate_checksum()` zeroes the checksum, asks the IPv6 parent for a pseudo-header, appends ICMP header bytes and child payload bytes, computes the checksum via `Header.compute_checksum()`, and stores it. Well-formedness checks known message type and valid code membership.

State and persistence behavior: State lives in the packet buffer and linked child payload; there is no persistence. Checksum calculation mutates the checksum field and requires the ICMP6 object to be attached below an IPv6 parent that implements `get_pseudo_header()`.

Dependencies and integration points: The module depends on `ImpactPacket.Header`, `ImpactPacket.Data`, `array_tobytes`, `IP6_Address`, `array`, and `struct`. It integrates with `ImpactDecoder.ICMP6Decoder`, `IP6.get_pseudo_header()`, and packet building code that composes IPv6/extension-header/ICMPv6 trees.

Risks: `__str__()`, code-description lookup, and `is_well_formed()` can raise `KeyError` for unknown message types because some lookups happen before all validation. `set_target_address()` calls `address.get_bytes()`, but `IP6_Address` exposes `as_bytes()`, suggesting a latent bug. `get_note_information_data()` has a typo in the method name. Factory methods do not calculate checksums automatically, so callers must attach to IPv6 and call `calculate_checksum()`.

Test signals: Tests should cover factory output layouts, checksum calculation under an IPv6 parent, validation of known/unknown type-code pairs, neighbor flag bit operations, node-information flag operations, echo field accessors, and the target-address setter path.
