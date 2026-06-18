# sources/storage-engines/foundationdb/flow/include/flow/IPAddress.h

## Purpose
`IPAddress.h` defines a compact IPv4/IPv6 address value type with parsing, formatting, ordering, tracing, and serialization support.

## Important APIs, Types, And Functions
`IPAddress` stores either a `uint32_t` IPv4 address or 16-byte `IPAddressStore` IPv6 address. It exposes `isV6()`, `isV4()`, `isValid()`, `toV4()`, `toV6()`, `toString()`, `parse()`, comparison operators, `serialize()`, and `Traceable<IPAddress>`.

## Control Flow
Parsing and formatting are implemented out of line. Serialization either uses generic function-serializer support for the variant or writes a bool tag followed by v4/v6 bytes for older serializers.

## State And Persistence Behavior
The object persists address bytes only; IPv4 uses the first alternative and IPv6 uses the 16-byte array. Serialized form includes address family, preserving compatibility with non-fb serializers.

## Dependencies And Integration Points
It depends on `ObjectSerializerTraits`, `Optional`, `Traceable`, arrays, and variants. It integrates into `NetworkAddress`, DNS resolution, tracing, and configuration parsing.

## Risks And Edge Cases
Callers must only call `toV4()` or `toV6()` after checking family. IPv4 byte order must match parser/formatter and Boost.Asio conversions. Variant serialization compatibility is important for persisted network addresses.

## Test Signals
Parse/format round trips for IPv4 and IPv6, invalid strings, ordering, serializer round trips across both serializer paths, trace formatting, and Boost byte-layout static assertions are key.
