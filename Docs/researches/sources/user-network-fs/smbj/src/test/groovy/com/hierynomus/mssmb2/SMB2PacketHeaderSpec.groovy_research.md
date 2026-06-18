# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/SMB2PacketHeaderSpec.groovy
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/SMB2PacketHeaderSpec.groovy

Purpose: verifies SMB2 header writing of credit request for selected dialects. Important APIs are `SMB2PacketHeader.setCreditRequest`, `setCreditCharge`, `setDialect`, `setMessageType`, and `writeTo(SMBBuffer)`. Control flow writes a negotiate header for SMB 2.1, 2.0.2, and 2XX, seeks to byte offset 14, and checks the 16-bit credit request value.

State and persistence: no persisted state; one header and buffer per iteration. Integration point is SMB2 wire header generation. Risk covered is dialect-dependent header field placement, especially credit request versus channel sequence behavior. Test signal is good for this field but not full header layout.
