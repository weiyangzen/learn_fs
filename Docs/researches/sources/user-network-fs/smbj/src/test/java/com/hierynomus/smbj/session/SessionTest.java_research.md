# sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/session/SessionTest.java
# sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/session/SessionTest.java

Purpose: JUnit tests for session/share/file behavior. It asserts share names cannot contain backslashes and verifies `Session.open` defaults to `SMB2CreateDisposition.FILE_OPEN` when no create disposition is provided by inspecting the `SMB2CreateRequest` passed to a mocked share.

State and persistence: session object with mocked connection/share responses; no persistence. Dependencies are session, disk share/file open APIs, SMB create messages, and Mockito answers. Integration point is application-level share and file open calls. Risks covered include invalid share path injection and accidental default create-disposition changes that could create/truncate files. Test signal is focused but protects a dangerous default.
