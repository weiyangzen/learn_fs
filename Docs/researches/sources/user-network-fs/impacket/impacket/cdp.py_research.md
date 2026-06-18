# sources/user-network-fs/impacket/impacket/cdp.py

## Purpose

`cdp.py` decodes Cisco Discovery Protocol packets and their TLV elements. It exposes a `CDP` header class, TLV element classes for known CDP types, address-detail parsing, basic byte-reading helpers, and a factory that maps TLV type numbers to element classes.

## Important APIs, Types, and Functions

`CDPTypes` names common TLV type constants. `CDP` subclasses `ImpactPacket.Header` and parses version, TTL, checksum, packet type/length, and TLV elements. `CDPElement` is the base TLV class with `Get_length`, `get_length`, `get_data`, and an IP-address helper.

Known TLV classes include `CDPDevice`, `Address`, `AddressDetails`, `Port`, `Capabilities`, `SoftVersion`, `Platform`, `IpPrefix`, `ProtocolHello`, `VTPManagementDomain`, `Duplex`, `VLAN`, `TrustBitmap`, `UntrustedPortCoS`, `ManagementAddresses`, `MTU`, `SystemName`, `SystemObjectId`, and `SnmpLocation`. `DummyCdpElement` represents unknown TLVs. `CDPElementFactory.create` chooses an element class from `elementTypeMap`.

## Control Flow

When `CDP` receives a buffer, it loads the fixed header and calls `_getElements`. That strips the fixed header bytes and repeatedly creates a TLV element from the remaining buffer, advances by `elem.get_length()`, and stops when no bytes remain. `Address` elements further parse address-detail records from their payload. `Capabilities` lazily decodes bit flags from its four-byte payload during initialization.

## State and Persistence Behavior

The module is read-only and in-memory. Parsed `CDP` instances hold `_elements`; parsed `Address` instances hold `address_details`; `Capabilities` stores decoded boolean flags. There is no packet construction path beyond inherited byte buffers and no filesystem or network persistence.

## Dependencies and Integration Points

The module depends on `struct.unpack`, `socket.inet_ntoa`, `impacket.ImpactPacket.Header`, `array_tobytes`, and package `LOG`. It integrates with packet capture decoders that dispatch CDP payloads to this class and with `ImpactPacket` printable header behavior.

## Risks and Edge Cases

The parser assumes TLV lengths are well-formed. If a TLV length is zero or smaller than the header, `_getElements` can loop incorrectly or slice malformed data. Several methods return bytes but concatenate with strings in `__str__`, which is risky under Python 3. `CDPElement.get_header_size` lacks a return statement. `Capabilities.is_host` returns the method object rather than `_host`. `get_word` uses signed `!h`, which can produce negative values for high-bit TLV types or lengths. Only IPv4 address details are rendered specially.

## Test Signals

Tests should parse representative CDP frames with device, port, platform, capabilities, IPv4 address, protocol hello, and unknown TLVs. Edge tests should cover truncated TLVs, zero/invalid lengths, signed type/length boundaries, `Capabilities` flag accessors, and Python 3 string/bytes formatting.
