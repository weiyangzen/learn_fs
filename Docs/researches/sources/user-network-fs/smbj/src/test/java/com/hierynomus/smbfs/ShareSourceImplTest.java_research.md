# sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbfs/ShareSourceImplTest.java
# sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbfs/ShareSourceImplTest.java

Purpose: tests `ShareSourceImpl`, the NIO filesystem bridge that supplies SMB share handles. It uses mocks to validate share retrieval, reuse, and close/disconnect behavior around `DiskShare` or session interactions.

State and persistence: in-memory mocked client/session/share references; no persistence. Dependencies are JUnit, Mockito, and smbfs/share abstractions. Integration point is `SmbFileSystem` access to SMBJ sessions and shares. Risks covered include leaking shares, returning stale references, and incorrect close delegation. Test signal is focused on adapter lifecycle behavior.
