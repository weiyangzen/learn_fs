# sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbfs/SmbFileSystemTest.java
# sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbfs/SmbFileSystemTest.java

Purpose: tests the NIO `SmbFileSystem` implementation. It validates root/path construction, separator behavior, open/closed state, provider/share accessors, supported file attribute views, and path factory behavior.

State and persistence: in-memory filesystem instance with close state and associated share source/provider references; no disk persistence. Dependencies are Java NIO `FileSystem` contracts, JUnit, Mockito, and smbfs classes. Integration point is Java `Files` APIs over SMB. Risks covered include NIO contract violations, incorrect separator/root behavior, and lifecycle misuse after close. Test signal is broad for filesystem object semantics.
