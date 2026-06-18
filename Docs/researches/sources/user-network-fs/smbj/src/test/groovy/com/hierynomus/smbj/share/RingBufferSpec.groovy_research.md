# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/share/RingBufferSpec.groovy
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/share/RingBufferSpec.groovy

Purpose: comprehensive tests for `RingBuffer` write/read behavior. It covers writing whole arrays, writing selected ranges, invalid range errors, single-byte appends, appending to existing data, wrap-around after reads, full-buffer exceptions, fixed-size reads, zero-length reads, reads larger than available data, size accounting, reuse after reads, and write-position wrap-around edge cases.

State and persistence: in-memory circular buffer state (`read`/`write` positions and size); no persistence. Dependencies are only Spock and byte arrays. Integration point is SMB share stream buffering. Risks covered are classic circular-buffer off-by-one, overflow, under-read, wrap-around split-copy, and zero-byte behavior. Test signal is strong for buffer correctness.
