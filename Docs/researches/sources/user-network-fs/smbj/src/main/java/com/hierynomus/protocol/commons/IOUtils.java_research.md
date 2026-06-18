# sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/IOUtils.java

## Purpose
Source file in package com.hierynomus.protocol.commons defining class IOUtils for the SMBJ user-network filesystem source tree.

## Important APIs / Types / Functions
Defines class `IOUtils` in package `com.hierynomus.protocol.commons`. Important methods/functions include `closeQuietly`, `closeSilently`. Important fields include `logger`. Source size: 48 lines.

## Control Flow
Control flow is simple delegation through the package's interface or data holder contract.

## State and Persistence
State fields observed: logger. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
External dependencies: org.slf4j.Logger, org.slf4j.LoggerFactory.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Compile-time contract tests and focused unit tests around public methods are the primary signal.
