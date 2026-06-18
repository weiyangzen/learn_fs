# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/SMB2ErrorSpec.groovy
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/SMB2ErrorSpec.groovy

Purpose: tests `SMB2Error.read` handling of empty error data. It builds minimal `SMBBuffer` payloads with status structure fields and zero byte count. One case includes the trailing reserved error-data byte; the Windows 10 1709 case omits it.

State and persistence: no state beyond a fresh header and buffer. Dependencies are `SMB2PacketHeader`, `SMB2Error`, and `SMBBuffer`. Integration point is SMB2 error packet decoding from servers that vary in reserved-byte emission. Risk covered is parser over-read or failure on zero-length error payloads. Test signal is narrow but important for compatibility with real Windows behavior.
