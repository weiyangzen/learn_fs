# sources/user-network-fs/impacket/impacket/dhcp.py

## Purpose

`dhcp.py` provides compact BOOTP and DHCP packet structures for Impacket. It models the fixed BOOTP header in `BootpPacket`, models the DHCP magic cookie and variable-length options in `DhcpPacket`, and exposes helpers for packing, unpacking, querying, and recognizing DHCP option values.

## Important APIs, Types, And Functions

`BootpPacket` inherits both `ProtocolPacket` and `structure.Structure` and declares `commonHdr` fields for op, hardware type/length, transaction id, timing/flags, client/your/server/gateway addresses, client hardware address, server name, and boot filename. The dynamic `_chaddr`/`chaddr` fields use Impacket `Structure` expressions so the stored hardware address length follows `hlen`.

`DhcpPacket` defines protocol constants for `MAGIC_NUMBER`, BOOTREQUEST/BOOTREPLY, and DHCP message types. Its `options` mapping is the core API: option names map to numeric option code plus Impacket structure format, including scalar network-order integers, variable byte strings (`:`), repeated integer lists (`*!L`, `*!H`), pad/eof pseudo-options, and common DHCP extensions such as FQDN, domain search, classless routes, and proxy autoconfig. The structure serializes `cookie`, then `_options` through `packOptions(options)`, and exposes decoded `options` through `unpackOptions(_options)`.

Public behavior is concentrated in `packOptions()`, `getOptionNameAndFormat()`, `unpackOptions()`, `unpackParameterRequestList()`, `isAskingForProxyAutodiscovery()`, and `getOptionValue()`.

## Control Flow

For building packets, callers populate `DhcpPacket['options']` as `(name, value)` tuples. `Structure` invokes `packOptions()`, looks up code and format, packs each value with `self.pack()`, and emits type/length/value bytes. For parsing, `Structure` reads the raw option tail into `_options`, then `unpackOptions()` iterates through the bytearray, resolves each numeric option to a known name or leaves the numeric code as the name, reads the next byte as the option length, unpacks the following bytes with the selected format, and advances by `2 + size`. Higher-level queries scan the decoded `fields['options']` list.

## State And Persistence

The module has no persistence. Parsed state lives in each `Structure` instance's `fields`, including the decoded options list. It does not track DHCP lease state, retransmissions, sockets, timers, or client/server state machines; it is only a packet representation layer.

## Dependencies And Integration Points

The implementation depends on `impacket.structure.Structure` for declarative packing/unpacking and on `ImpactPacket.ProtocolPacket` for packet composition compatibility. It is intended to integrate with network tooling that builds or inspects UDP DHCP payloads, especially code that needs direct option-level access without implementing a full DHCP agent.

## Risks And Edge Cases

Pad option `0` and end option `255` are listed as zero-length formats, but `unpackOptions()` always reads the following byte as a size, so true RFC pad/end handling is limited. `unpackParameterRequestList()` and `isAskingForProxyAutodiscovery()` call `ord()` on option bytes; in Python 3 iteration over a `bytes` object yields integers, so callers may hit type errors depending on the decoded representation. Option packing does not automatically append the DHCP end marker. Unknown option codes are preserved as numeric names with raw `:` data, which is useful but means later `packOptions()` cannot re-emit them unless the numeric key is added to `options`. Bounds checking is minimal for truncated option buffers.

## Test Signals

Tests should round-trip BOOTP fields, pack and unpack common DHCP options (`message-type`, `server-id`, `requested-ip`, `parameter-request-list`, repeated DNS/router addresses), preserve unknown options, and verify behavior around pad/eof/truncated option tails. A focused regression test for proxy-autodiscovery option `252` should cover Python 3 bytes semantics. Integration tests can build a DISCOVER or OFFER payload and compare bytes against known captures.
