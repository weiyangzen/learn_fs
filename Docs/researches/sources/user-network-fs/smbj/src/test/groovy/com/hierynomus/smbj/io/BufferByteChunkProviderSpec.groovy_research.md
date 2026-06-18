# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/io/BufferByteChunkProviderSpec.groovy
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/io/BufferByteChunkProviderSpec.groovy

Purpose: validates `BufferByteChunkProvider` over `Buffer.PlainBuffer`. It checks empty availability, available-byte counting after writes, full reads into arrays, partial reads when fewer bytes remain than requested, and no-op behavior when nothing is left.

State and persistence: provider consumes an in-memory protocol buffer; no persistence. Dependencies are `Buffer`, `Endian`, and byte chunk provider APIs. Integration point is SMB write/upload streaming from protocol buffers. Risks covered include read-position advancement, partial final chunk handling, and zero-byte reads. Test signal is focused on buffer-backed chunk semantics.
