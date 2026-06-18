# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/io/InputStreamByteChunkProviderSpec.groovy
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/io/InputStreamByteChunkProviderSpec.groovy

Purpose: tests lifecycle behavior of `InputStreamByteChunkProvider`. It constructs the provider around a Spock `InputStream` mock, closes the provider, and verifies the underlying stream is closed exactly once.

State and persistence: provider owns an input stream reference; no persistence. Dependencies are Java `InputStream` and Spock mocks. Integration point is SMB upload/write from arbitrary streams. Risk covered is resource leak on provider close. Test signal is narrow; it does not cover chunk reading, partial reads, or exception propagation.
