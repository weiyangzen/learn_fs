# sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/transport/PacketSerializer.java

## Purpose
Generic transport-layer contract or holder for packet IO. PacketSerializer helps connect protocol-neutral Packet/PacketData objects to serializers, receivers, factories, and connection implementations.

## Important APIs / Types / Functions
Defines interface `PacketSerializer` in package `com.hierynomus.protocol.transport`. Source size: 29 lines.

## Control Flow
Control flow is simple delegation through the package's interface or data holder contract.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.Packet, com.hierynomus.protocol.commons.buffer.Buffer.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Compile-time contract tests and focused unit tests around public methods are the primary signal.
