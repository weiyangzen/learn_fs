# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/messages/SMB2ChangeNotifyResponseSpec.groovy
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/messages/SMB2ChangeNotifyResponseSpec.groovy

Purpose: tests parsing of `SMB2ChangeNotifyResponse` packets. It decodes a captured response and asserts five `FileNotifyInfo` file names, including alternate data stream style names and a metadata name with unusual UTF-16 content. A second captured packet with `STATUS_NOTIFY_CLEANUP` asserts an empty notification list.

State and persistence: transient packet data only. Dependencies are `ByteArrayUtils`, `AbstractPacketReadSpec`, and change-notify model classes. Integration point is watch/change notification behavior for SMB shares. Risks covered include linked notification records, Unicode file-name decoding, cleanup status handling, and zero-output cases. Test signal is strong for parser resilience against real server payloads.
