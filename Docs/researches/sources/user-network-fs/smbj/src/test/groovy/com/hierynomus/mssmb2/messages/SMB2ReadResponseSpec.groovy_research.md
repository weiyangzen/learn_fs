# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/messages/SMB2ReadResponseSpec.groovy
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/messages/SMB2ReadResponseSpec.groovy

Purpose: tests SMB2 read response decoding. It parses a large captured read response containing log-like byte data and asserts the decoded `dataLength` is 21401. It also parses an EOF response and verifies the header status is `NtStatus.STATUS_END_OF_FILE.value`.

State and persistence: transient parsed packets only. Dependencies are `NtStatus`, `ByteArrayUtils`, and the shared packet converter. Integration point is file read response handling, especially large payload lengths and EOF status propagation. Risks covered include data-offset/data-length interpretation, payload preservation independent of textual contents, and correct non-success status decoding. Test signal is good for these two response shapes.
