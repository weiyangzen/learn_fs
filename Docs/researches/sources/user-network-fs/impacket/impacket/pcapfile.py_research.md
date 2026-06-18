# sources/user-network-fs/impacket/impacket/pcapfile.py

## Purpose
`pcapfile.py` provides a lightweight classic pcap reader/writer built on Impacket `Structure`. It models the global pcap header, per-packet records, and a `PcapFile` wrapper that can read packets sequentially, write packet records, set snap length, set link type, and iterate all packets in a file.

## Important APIs, Types, and Functions
`PCapFileHeader` describes the pcap global header with magic, version 2.4, GMT correction, time accuracy, snap length, link type, and an unused `packets` list field. `PCapFilePacket` describes each record with seconds, microseconds, saved length, real length, and payload data; its constructor initializes `data` to empty bytes.

`PcapFile` is the main API. It accepts an optional filename and mode, or a caller can inject a file-like object with `setFile()`. It exposes `reset()`, `close()`, `fileno()`, `setSnapLen()`, `getSnapLen()`, `setLinkType()`, `getLinkType()`, `readHeaderOnce()`, `createHeaderOnce()`, `writeHeaderOnce()`, `read()`, `write()`, and `packets()`. Offset constants such as `O_ETH`, `O_IP`, `O_UDP`, and `O_UDP_DATA` are convenience layer indexes used by older packet-handling code.

## Control Flow
For reading, `read()` lazily parses the global header on the first call through `readHeaderOnce()`, then tries to parse a `PCapFilePacket` from the current file position and read `savedLength` bytes of payload. Any exception returns `None`, which acts as EOF or parse-failure sentinel. `packets()` calls `reset()` and repeatedly yields `read()` results until `None`.

For writing, setters call `createHeaderOnce()` so header fields can be modified before output. `write()` calls `writeHeaderOnce()`, which seeks to offset zero, creates a default header if needed, writes the header once, and marks `wroteHeader`. It then writes the packet bytes. The wrapper assumes callers pass a `PCapFilePacket` or compatible `Structure` instance with `getData()`/string conversion behavior.

## State and Persistence Behavior
`PcapFile` persists bytes to the file object supplied by filename or `setFile()`. It tracks `self.hdr` as the parsed or created global header and `self.wroteHeader` to avoid rewriting the header after the first packet write. `reset()` clears `hdr` and seeks the file to zero but does not reset `wroteHeader`, so read-after-write workflows need care if they reuse the same object.

## Dependencies and Integration Points
The module depends on `impacket.structure`. It integrates with `pcap_linktypes.py` by convention through the numeric `linkType` field, defaulting to Ethernet (`1`). Packet payloads are opaque bytes, so higher layers such as `ImpactPacket`/`ImpactDecoder` are responsible for interpreting Ethernet, IP, TCP, UDP, ICMP, ARP, or other link-layer formats.

## Risks and Edge Cases
The magic string is expressed as a Python string literal rather than bytes, and `write()` uses `str(pkt)` rather than `pkt.getData()`, which can be problematic under Python 3 if `Structure.__str__` does not return raw bytes for a specific object. `read()` catches all exceptions and returns `None`, hiding truncated headers, malformed records, permission errors, and genuine EOF behind the same signal. Endianness is fixed to little-endian classic pcap; swapped-endian, nanosecond, or pcapng files are not supported. There is no context-manager support and no validation that `savedLength` is within snap length or remaining file size.

## Test Signals
Tests should create a temporary binary pcap, set snap length/link type, write one or more `PCapFilePacket` records, reopen and verify header fields and payload bytes. Additional signals include empty file returns `None`, truncated record returns `None`, `packets()` resets iteration to the first packet, file-like injection works, and non-Ethernet link types round-trip. Python 3 tests should specifically assert that `write()` emits bytes and does not stringify packet objects incorrectly.
