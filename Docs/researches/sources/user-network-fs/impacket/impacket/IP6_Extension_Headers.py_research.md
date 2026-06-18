# sources/user-network-fs/impacket/impacket/IP6_Extension_Headers.py

Purpose: `IP6_Extension_Headers.py` implements IPv6 extension-header classes and option buffers for Hop-by-Hop Options, Destination Options, and Routing Options. It also provides the registry used by the IPv6 decoder to map next-header values to decoder classes.

Important APIs, types, and functions: `IP6_Extension_Header` handles common next-header/header-ext-len fields, option loading, packet serialization, child linking, pseudo-header delegation, and subclass registry discovery through `get_extension_headers()`. `Extension_Option` handles generic option type, option length, data, and size. `Option_PAD1` and `Option_PADN` model padding. `Basic_Extension_Header` adds automatic 8-octet padding for option headers. `Hop_By_Hop`, `Destination_Options`, and `Routing_Options` define header type values and decoder lookups; `Routing_Options` adds routing type and segments-left fields.

Control flow: Base construction initializes common header fields and option list, then either parses a buffer or calls `reset()`. `load_header()` reads the fixed fields, computes the full extension header length as `(Hdr Ext Len + 1) * 8`, and parses only Pad1 and PadN options into `_option_list`. `Basic_Extension_Header.add_option()` removes current padding, appends the new option, then adds Pad1/PadN to maintain 8-byte alignment. `get_packet()` updates `Header Ext Len`, serializes fixed fields and options, and appends child data if present.

State and persistence behavior: State is the mutable header buffer, `_option_list`, and for `Basic_Extension_Header` the `padded` flag. There is no persistence. Attaching another extension header through `contains()` updates the next-header field.

Dependencies and integration points: The module depends on `ImpactPacket.Header`, `ImpactPacketException`, and `PacketBuffer`. Decoder lookups import `ImpactDecoder` lazily to avoid import cycles. It integrates with `IP6.contains()`, `IP6.get_pseudo_header()`, and `ImpactDecoder.IP6MultiProtocolDecoder`.

Risks: `load_header()` only materializes padding options; unknown extension options are treated as PadN-shaped buffers and lose their type/data semantics. The `Extension_Option` maximum-size exception string has malformed formatting text. `Option_PADN.OPTION_DESCRIPTION` comment says Pad1. `Basic_Extension_Header.add_padding()` uses recursive `add_option()` through overridden dispatch but relies on the `padded` flag to terminate. `get_header_size()` is based on parsed options, so malformed buffers with unsupported options may produce misleading sizes.

Test signals: Tests should cover padding insertion for option lengths, packet serialization updating `Header Ext Len`, parsing truncated packets, extension-header registry contents, child next-header propagation, routing-options field accessors, and unknown option handling expectations.
