# sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/InputSubstream.java

Purpose: `InputSubstream` exposes a bounded byte range from an underlying `InputStream` without closing the underlying stream when the substream is closed. It is useful for tests that need range reads or multipart stream slices.

Important APIs and types: The class extends `FilterInputStream` and overrides `read()`, `read(byte[], int, int)`, `mark`, `reset`, `close`, and `available`. Constructor arguments are the wrapped stream, a skip offset, and requested length.

Control flow: On first read, it repeatedly calls `skip` until `currentPosition` reaches `requestedSkipOffset`, failing after `MAX_SKIPS` zero-length skips. It then computes remaining bytes as `skip + length - currentPosition`, caps the requested read length, reads from the delegate, and updates `currentPosition`. `mark` and `reset` preserve the logical current position.

State and persistence behavior: Runtime state includes `currentPosition`, `requestedSkipOffset`, `requestedLength`, and `markedPosition`. There is no persistence. `close` is intentionally a no-op to leave the wrapped stream open.

Dependencies and integration points: It depends only on Java IO and is likely used by tests validating range transfer, upload/download offsets, or stream lifecycle behavior.

Risks: If the wrapped stream returns `-1`, `currentPosition += bytesRead` can decrement by one; callers usually avoid reading past EOF, but this is a subtle edge case. Repeated zero skips can fail on streams with unusual skip behavior. No constructor validation prevents negative skip or length.

Test signals: Expected signals are reads limited to the requested range, underlying stream not closed by substream close, correct available count, and reset returning to marked logical position.
