# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/messages/AbstractPacketReadSpec.groovy
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/messages/AbstractPacketReadSpec.groovy

Purpose: shared Spock base for SMB2 message parser tests. It owns a `@Shared SMB2MessageConverter` and exposes `convert(byte[] bytes)`, which wraps bytes in `SMB2PacketData` and delegates to `converter.readPacket(null, packetData)`.

State and persistence: shared converter state only for the test instance; no persistence. Dependencies are `SMB2MessageConverter`, `SMB2PacketData`, and Spock. Integration point is every subclass that decodes raw captured SMB2 packets. Risk is that all parser specs inherit the same null request-packet context, so they primarily cover response parsing paths that do not need request correlation. Test signal is infrastructural.
