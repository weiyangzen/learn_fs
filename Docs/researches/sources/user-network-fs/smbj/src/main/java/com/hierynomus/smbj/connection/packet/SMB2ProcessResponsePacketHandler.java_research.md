# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/packet/SMB2ProcessResponsePacketHandler.java

Purpose: `SMB2ProcessResponsePacketHandler` deserializes final SMB2 responses and completes matching request promises.

Important APIs and control flow: it looks up the original request, asks `SMB2MessageConverter` to read the response packet in request context, removes the outstanding request by response message ID, and delivers the packet to the promise.

State, dependencies, and integration: terminal successful SMB2 handler in the chain. It depends on original request packet type for command-specific parsing.

Risks: deserialization failure throws `TransportException` but may leave the outstanding request unless caller handles connection error. Tests should cover successful delivery, converter failures, command mismatch behavior, and outstanding removal.
