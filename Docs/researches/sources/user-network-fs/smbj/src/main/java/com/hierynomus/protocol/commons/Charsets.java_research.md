# sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/Charsets.java

## Purpose
Source file in package com.hierynomus.protocol.commons defining class Charsets for the SMBJ user-network filesystem source tree.

## Important APIs / Types / Functions
Defines class `Charsets` in package `com.hierynomus.protocol.commons`. Important methods/functions include `Charsets`. Important fields include `UTF_8`, `UTF_16BE`, `UTF_16LE`, `UTF_16`, `US_ASCII`. Source size: 32 lines.

## Control Flow
Control flow is simple delegation through the package's interface or data holder contract.

## State and Persistence
State fields observed: UTF_8, UTF_16BE, UTF_16LE, UTF_16, US_ASCII. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
JDK/JCE dependencies: java.nio.charset.Charset.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Compile-time contract tests and focused unit tests around public methods are the primary signal.
