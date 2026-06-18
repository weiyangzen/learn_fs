# sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbfs/SmbDirectoryStreamTest.java
# sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbfs/SmbDirectoryStreamTest.java

Purpose: tests NIO directory stream behavior for SMB paths. It validates iteration over directory entries, filter behavior, close behavior, and exception handling around an SMB directory listing source.

State and persistence: transient mocked directory entries and stream closed state. Dependencies are Java NIO `DirectoryStream`, JUnit, Mockito, and smbfs path classes. Integration point is `Files.newDirectoryStream` over SMB shares. Risks covered include iterator reuse, close idempotence, filter application, and translating SMB/listing errors to NIO expectations. Test signal is useful for filesystem-provider compliance.
