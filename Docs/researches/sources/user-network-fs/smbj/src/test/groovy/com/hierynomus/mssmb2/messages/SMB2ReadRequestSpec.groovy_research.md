# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/messages/SMB2ReadRequestSpec.groovy
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/messages/SMB2ReadRequestSpec.groovy

Purpose: validates exact SMB2 read request serialization for byte-range lock compatibility. Important APIs are `SMB2ReadRequest` constructor, `getHeader().setMessageId`, and `write(SMBBuffer)`. Control flow builds file-id halves from hex, sets dialect/session/tree/message IDs, serializes a read at offset 0 with max payload 15, and compares both payload body and whole packet against expected hex.

State and persistence: no persisted state. Dependencies are `SMB2FileId`, `SMB2Dialect`, `SMBBuffer`, and byte utilities. Integration point is read request wire generation. Risk covered is requesting more than the exact user range, which can conflict with server byte-range locks. Test signal is precise but currently only one active row; a larger payload row is commented out.
