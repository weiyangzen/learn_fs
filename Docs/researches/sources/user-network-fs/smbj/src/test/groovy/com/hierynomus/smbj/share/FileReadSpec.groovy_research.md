# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/share/FileReadSpec.groovy
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/share/FileReadSpec.groovy

Purpose: integration-style tests for SMBJ remote file reads. Setup builds deterministic file bytes and expected digest, opens a file through a stub SMB transport, and responds to `SMB2ReadRequest` with slices from the backing byte array. Tests cover direct `read` loops, buffer offsets, input-stream reads, IBM JVM mode behavior, input-stream buffer offsets, and `skip` before/after reading.

State and persistence: transient file bytes, digest state, connection/session/share/file state. Dependencies include SMB read/create messages, `ByteArrayUtils`, digest streams, stub auth/transport, and packet processors. Risks covered include offset arithmetic, EOF handling, buffer-offset writes, skip semantics, and read payload sizing. Test signal is strong for high-level read APIs.
