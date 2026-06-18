# sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/OzoneInputStream.java

Purpose: This public input wrapper exposes Ozone key reads as a standard `InputStream` plus Hadoop `ByteBufferReadable`, `CanUnbuffer`, and `Seekable` interfaces when supported by the underlying stream.

Important APIs and types: It implements `read`, byte-array read, `read(ByteBuffer)`, `close`, `available`, `skip`, `getInputStream`, `unbuffer`, `seek`, `getPos`, and `seekToNewSource`. It delegates to `InputStream`, `ByteBufferReadable`, `CanUnbuffer`, and `Seekable`.

Control flow: Standard reads always delegate. ByteBuffer reads require the wrapped stream to implement `ByteBufferReadable`; seek methods require `Seekable`; unbuffer is optional and only invoked when supported.

State and persistence behavior: Runtime state is only the wrapped input stream reference. There is no persistence or buffering in this wrapper.

Dependencies and integration points: Returned by `ClientProtocol.getKey`, file reads, S3 key details readers, and replica-read APIs. It usually wraps `KeyInputStream` or `OzoneCryptoInputStream`.

Risks: The default constructor leaves `inputStream` null and is only safe for tests or serialization-like usage. Unsupported ByteBuffer or seek operations fail at runtime. Close is synchronized but other delegated operations are not.

Test signals: Tests should cover delegation of normal reads, ByteBuffer read support and unsupported exceptions, seek/getPos/seekToNewSource delegation, unbuffer optional behavior, and null default-constructor safety assumptions.
