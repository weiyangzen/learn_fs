
# sources/user-network-fs/rclone/backend/mailru/api/helpers.go

## Purpose
Provides binary protocol reader/writer helpers for the Mail.ru Cloud backend.

## Important APIs, Types, And Control Flow
`BinWriter` wraps a byte buffer and writes unsigned varints, signed-as-uvarint values, zero-terminated strings, raw buffers, and length-prefixed buffers. `BinReader` wraps a counting buffered reader, stores the first parse error, and exposes reads for bytes, shorts, little-endian uint16, uvarints, fixed byte counts, length-prefixed bytes, zero-terminated strings, and Unix dates. Parse errors set `err`; non-EOF parse errors also panic through `check`.

## State And Persistence
Reader state is current byte position and first error; writer state is accumulated request bytes. No external persistence.

## Dependencies And Integration Points
Uses `encoding/binary`, `bufio`, rclone `readers.CountingReader`, and Mail.ru binary constants. Higher-level API code uses these helpers to serialize operations and parse opaque binary responses.

## Risks And Test Signals
Risks include panic-on-malformed-response behavior, partial `Read` handling with `bufio.Reader.Read`, unchecked large lengths causing allocations, uvarint treatment of signed values, and zero-termination validation. Tests should cover malformed EOF, invalid length, nonzero terminator, count tracking, and round-trip writer/reader sequences.
