# sources/user-network-fs/impacket/impacket/wps.py

## Purpose

`wps.py` implements packet helpers for Wi-Fi Protected Setup Simple Configuration data. It provides TLV builders/parsers, WPS element and value constants, and a `SimpleConfig` protocol packet wrapper.

## Important APIs, Types, And Functions

Builder classes are `ArrayBuilder`, `ByteBuilder`, `StringBuilder`, and `NumBuilder`. `TLVContainer` stores ordered TLV pairs and exposes `append()`, typed iteration, `all()`, `first()`, `to_ary()`, `get_packet()`, `n2ary()`, and `ary2n()`. Constant classes include `SCElem`, `MessageType`, `AuthTypeFlag`, `EncryptionTypeFlag`, `ConnectionTypeFlag`, `ConfigMethod`, `OpCode`, `AssocState`, `ConfigError`, `DevicePasswordId`, and `WpsState`. `SimpleConfig` extends `ProtocolPacket` and defines opcode/flag fields plus `BUILDERS`.

## Control Flow

`TLVContainer.from_ary()` scans input as big-endian type, big-endian length, and raw value bytes. Iteration converts values through registered builders. Serialization emits stored type, length, and raw value arrays. `SimpleConfig.build_tlv_container()` returns a configured container with descriptions derived from `SCElem`.

## State And Persistence Behavior

There is no persistence. `TLVContainer` keeps mutable `elems`, optional descriptions, and an optional parent pointer. Builders are stateless except for `NumBuilder.size`.

## Dependencies And Integration Points

It depends on `array`, `struct`, `functools.reduce`, `impacket.ImpactPacket.array_tobytes`, and `impacket.helper.ProtocolPacket`, `Byte`, and `Bit`. It integrates with wireless packet code that needs WPS attributes in EAP/WSC contexts.

## Risks And Edge Cases

`from_ary()` does not validate truncated headers or length overruns. `first()` raises `IndexError` for absent elements. `NumBuilder.to_ary()` does not explicitly reject negative input. `StringBuilder.to_ary()` expects bytes-like values. `AssocState.FAILURE` is accidentally a tuple. `PUBLIC_KEY` is mapped to `NumBuilder(192)`, treating it as a huge integer rather than raw bytes. Fragmentation and length-field behavior are explicitly unsupported.

## Test Signals

Tests should round-trip byte, string, numeric, and unknown TLVs; check duplicate/order behavior; cover absent `first()`, truncation, numeric overflow/negative values, `SimpleConfig` flag bits, and representative WPS M1/M2 attributes.
