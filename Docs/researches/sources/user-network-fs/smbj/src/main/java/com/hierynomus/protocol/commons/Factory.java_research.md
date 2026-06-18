# sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/Factory.java

## Purpose
Source file in package com.hierynomus.protocol.commons defining interface Factory for the SMBJ user-network filesystem source tree.

## Important APIs / Types / Functions
Defines interface `Factory` in package `com.hierynomus.protocol.commons`. Important methods/functions include `create`, `get`, `getNames`. Source size: 105 lines.

## Control Flow
Control flow is simple delegation through the package's interface or data holder contract.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
JDK/JCE dependencies: java.util.LinkedList, java.util.List.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Compile-time contract tests and focused unit tests around public methods are the primary signal.
