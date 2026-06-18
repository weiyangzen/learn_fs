# sources/user-network-fs/impacket/impacket/IP6.py

Purpose: `IP6.py` implements an IPv6 header class for Impacket packet trees. It exposes header field accessors, address setters/getters, extension-header-aware child linking, and pseudo-header construction for upper-layer checksums.

Important APIs, types, and functions: `IP6` defines ethertype `0x86DD`, 40-byte header size, and version 6. Accessors cover version, traffic class, flow label, payload length, next header, hop limit, source address, and destination address. Setters modify the same fields in the underlying byte buffer. `contains()` updates the IPv6 next-header field when the child is an `IP6_Extension_Header`. `get_pseudo_header()` builds the checksum pseudo-header and walks extension-header children to find the final upper-layer protocol and adjusted length. Deprecated aliases log warnings and call the newer address/version APIs.

Control flow: Construction initializes a 40-byte header and sets version 6 before optional load. Pseudo-header construction obtains source/destination bytes, starts with payload length and current next-header, subtracts each extension header's size while following child links, and serializes length, reserved bytes, and protocol number into an `array('B')`.

State and persistence behavior: State is the packet buffer plus parent/child links managed by `ImpactPacket.Header`. There is no persistence. Mutator methods directly alter the buffer; `contains()` can implicitly change next-header state.

Dependencies and integration points: The class depends on `ImpactPacket.Header`, `array_frombytes`, `IP6_Address`, `IP6_Extension_Header`, `struct`, `array`, and `LOG`. It is used by `ImpactDecoder.IP6Decoder`, ICMPv6 checksum calculation, Ethernet decoders for ethertype dispatch, and packet builders.

Risks: `get_pseudo_header()` has a FIXME for routing-header destination-address special handling. Payload length is not automatically synchronized when children are attached. `set_ip_src()` and `set_ip_dst()` assign `address.as_bytes()` into a mutable byte array; callers passing unusual array types should be covered. Deprecated methods still exist but only warn.

Test signals: Tests should cover bitfield packing/unpacking for traffic class and flow label, source/destination parsing, next-header updates when extension headers are attached, pseudo-header output with and without extension headers, and checksum integration with ICMPv6.
