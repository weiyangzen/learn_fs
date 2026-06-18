# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/messages/SMB2TreeConnectResponseSpec.groovy
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/messages/SMB2TreeConnectResponseSpec.groovy

Purpose: validates `SMB2TreeConnectResponse` parsing from captured bytes. The test asserts empty share capabilities, maximal access mask conversion to `AccessMask` enum set from `0x001f01ff`, share flags conversion from `0x800`, and disk-share classification.

State and persistence: none beyond parsed response. Dependencies are `AccessMask`, `SMB2ShareCapabilities`, `SMB2ShareFlags`, `EnumWithValue`, and the converter base. Integration point is share connection setup and capability/access interpretation. Risks covered include access-mask enum conversion, share-flag parsing, and correct share-type helper behavior. Test signal is focused on one normal tree-connect response.
