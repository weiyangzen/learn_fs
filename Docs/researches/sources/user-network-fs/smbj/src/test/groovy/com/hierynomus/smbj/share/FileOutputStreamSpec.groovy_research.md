# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/share/FileOutputStreamSpec.groovy
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/share/FileOutputStreamSpec.groovy

Purpose: integration-style tests for SMBJ `File` output stream behavior. Setup authenticates through a stub transport, opens a remote file with create/write options, and uses packet processor callbacks to return create and write responses. Tests verify closing after a `PrintWriter` close and closure after Groovy `withWriter`.

State and persistence: transient SMB connection/session/share/file state and a `ByteArrayOutputStream` sink; no real remote persistence. Dependencies include SMB create/write messages, `SMBClient`, `SmbConfig`, auth context, stub transport/auth, and `DiskShare`. Risks covered include stream/writer close ordering, file-handle close behavior, and write response handling. Test signal is good for high-level output-stream lifecycle but not broad write error handling.
