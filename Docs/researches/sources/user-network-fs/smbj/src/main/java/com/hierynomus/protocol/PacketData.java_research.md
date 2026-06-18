# sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/PacketData.java

## Purpose
Source file in package com.hierynomus.protocol defining interface PacketData for the SMBJ user-network filesystem source tree.

## Important APIs / Types / Functions
Defines interface `PacketData` in package `com.hierynomus.protocol`. Source size: 26 lines.

## Control Flow
Control flow is simple delegation through the package's interface or data holder contract.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.buffer.Buffer.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Compile-time contract tests and focused unit tests around public methods are the primary signal.
