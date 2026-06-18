# sources/user-network-fs/rclone/lib/readers/pattern_reader_test.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/pattern_reader_test.go -->
## sources/user-network-fs/rclone/lib/readers/pattern_reader_test.go

Purpose: validates deterministic pattern generation and seek behavior.

Important APIs and control flow: `TestPatternReader` checks zero-length and ten-byte streams, EOF behavior, and expected byte values. `TestPatternReaderSeek` reads a 1024-byte reference, validates modulo 251 content, seeks from start/current/end, verifies subsequent reads match the reference slices, and checks invalid whence and negative seek errors.

State, dependencies, and integration: dependencies are `io`, `testing`, and testify. The test uses full reads as reference data for later seek checks.

Risks and test signals: strong coverage for deterministic output and seek offset recalculation. It does not test seeking beyond the end.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/pattern_reader_test.go -->
