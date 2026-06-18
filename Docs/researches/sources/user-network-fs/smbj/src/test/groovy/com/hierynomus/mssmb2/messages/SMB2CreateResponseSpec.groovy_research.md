# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/messages/SMB2CreateResponseSpec.groovy
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/messages/SMB2CreateResponseSpec.groovy

Purpose: validates `SMB2CreateResponse` decoding. One captured packet lacks maximal content and asserts `FileTime` creation time plus persistent handle bytes from `fileId`. Another captured packet has `STATUS_PENDING` and asserts the converter still returns an `SMB2CreateResponse` with the pending status code.

State and persistence: no state beyond parsed packets. Dependencies include `FileTime`, `NtStatus`, `ByteArrayUtils`, and the shared converter base. Integration point is file open/create response parsing and async/pending create semantics. Risks covered are incomplete context payloads, handle extraction, timestamp conversion, and non-success status packets still mapping to the expected message type.
