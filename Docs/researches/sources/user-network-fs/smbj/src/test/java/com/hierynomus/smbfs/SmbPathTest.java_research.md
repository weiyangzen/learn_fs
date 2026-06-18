# sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbfs/SmbPathTest.java
# sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbfs/SmbPathTest.java

Purpose: detailed NIO `SmbPath` contract tests. It covers equality across filesystem/root/name combinations, string rendering with backslashes, parsing slash/backslash inputs, invalid empty path elements, filesystem/root/file-name/parent/name-count/name/subpath accessors, absolute detection, startsWith/endsWith, resolve, resolveSibling, relativize, and invalid relativize cases.

State and persistence: immutable path instances backed by an in-memory `SmbFileSystem`; no persistence. Dependencies are JUnit 5, Guava `EqualsTester`, Mockito, and Java NIO path semantics. Integration point is all smbfs path operations used by `Files`. Risks covered include absolute/relative mixing, root boundaries, separator normalization, parent/subpath indexing, and relativize correctness. Test signal is strong.
