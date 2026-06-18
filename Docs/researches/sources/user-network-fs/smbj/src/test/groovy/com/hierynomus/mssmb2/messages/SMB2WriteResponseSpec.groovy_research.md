# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/messages/SMB2WriteResponseSpec.groovy
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/messages/SMB2WriteResponseSpec.groovy

Purpose: tests decoding of `SMB2WriteResponse` from raw SMB2 bytes. Control flow uses the shared converter and asserts the message class and `bytesWritten == 8192`.

State and persistence: no state. Dependencies are byte parsing utilities and SMB2 message converter infrastructure. Integration point is SMB write completion handling. Risk covered is correct extraction of the count field from the write response body and class dispatch from command code. Test signal is narrow but directly protects upload/write accounting behavior.
