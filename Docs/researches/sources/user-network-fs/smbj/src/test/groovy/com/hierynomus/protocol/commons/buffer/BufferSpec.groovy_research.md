# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/protocol/commons/buffer/BufferSpec.groovy
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/protocol/commons/buffer/BufferSpec.groovy

Purpose: core buffer behavior tests for `Buffer.PlainBuffer`. It covers unsigned integer read/write for multiple sizes and both endian modes, out-of-range write exceptions, too-large uint64 read exceptions, string write/read using named charsets, and `InputStream` unsigned-byte behavior.

State and persistence: each case uses a fresh in-memory buffer. Dependencies are `Endian`, `Buffer`, Java `Charset`, and Spock data tables. Integration point is nearly all SMB/MS protocol serialization and parsing. Risks covered include endian mistakes, unsigned range validation, overflow handling, charset length handling, and sign extension when reading bytes via stream APIs. Test signal is broad and foundational for wire-format correctness.
