# sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbfs/SmbFileSystemProviderTest.java
# sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbfs/SmbFileSystemProviderTest.java

Purpose: comprehensive JUnit/Mockito tests for the NIO `SmbFileSystemProvider`. It covers missing filesystem errors, invalid share URIs, filesystem creation through a factory, parsing authentication context from URI credentials, environment override precedence, `char[]` passwords, invalid password types, duplicate filesystem keys, password-insensitive keying, unrelated filesystem creation, lookup/removal, and path/root resolution from URIs.

State and persistence: provider maintains an in-memory filesystem registry keyed by URI identity; mocks capture auth contexts. Dependencies are Java NIO exceptions, URI parsing, `SMBClient.DEFAULT_PORT`, Mockito captors, and provider constants. Integration point is `FileSystems.newFileSystem`/`getFileSystem`/`getPath`. Risks covered include credential parsing, URL decoding, password leakage into keys, registry lifecycle, and path extraction.
