# sources/user-network-fs/rclone/lib/readers/pattern_reader.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/pattern_reader.go -->
## sources/user-network-fs/rclone/lib/readers/pattern_reader.go

Purpose: creates deterministic byte streams for tests and integrity checks without storing large buffers.

Important APIs and control flow: `NewPatternReader(length)` returns an `io.ReadSeeker`. `Read(p)` fills bytes with a repeating sequence modulo 251 until `offset >= length`, then returns `io.EOF`. `Seek` supports standard whence values, rejects invalid whence and negative absolute positions, and recalculates the next byte from `abs % 251`.

State, dependencies, and integration: state is `offset`, total `length`, and current byte `c`. It depends on `errors` and `io`. It is used by pool/RW and context-reader tests to generate predictable content.

Risks and test signals: seeking past `length` is allowed and will cause immediate EOF on read, which matches some reader conventions but not all. No synchronization is provided. Tests cover empty, fixed-length reads, byte sequence, valid seeks, and seek errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/pattern_reader.go -->
