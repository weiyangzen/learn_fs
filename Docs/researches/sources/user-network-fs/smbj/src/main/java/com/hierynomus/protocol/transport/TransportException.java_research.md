# sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/transport/TransportException.java

## Purpose
Generic transport-layer contract or holder for packet IO. TransportException helps connect protocol-neutral Packet/PacketData objects to serializers, receivers, factories, and connection implementations.

## Important APIs / Types / Functions
Defines class `TransportException` in package `com.hierynomus.protocol.transport`. Important methods/functions include `wrap`, `TransportException`. Important fields include `Wrapper`. Source size: 45 lines.

## Control Flow
Control flow is simple delegation through the package's interface or data holder contract.

## State and Persistence
State fields observed: Wrapper. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.concurrent.ExceptionWrapper. JDK/JCE dependencies: java.io.IOException.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Compile-time contract tests and focused unit tests around public methods are the primary signal.
