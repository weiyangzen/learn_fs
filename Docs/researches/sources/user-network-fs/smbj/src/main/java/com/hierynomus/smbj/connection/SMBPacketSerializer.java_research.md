# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/SMBPacketSerializer.java

Purpose: `SMBPacketSerializer` adapts SMB packet objects to transport buffers.

Important APIs and control flow: `write` creates an `SMBBuffer`, asks the packet to serialize itself, and returns the buffer.

State, dependencies, and integration: stateless; passed into `PacketHandlers` by `Connection` transport setup.

Risks: all serialization errors occur inside packet write logic. Tests should verify it returns the exact bytes emitted by representative SMB1, SMB2, signed, and encrypted packet wrappers.
