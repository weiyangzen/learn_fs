# sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/ByteArrayUtils.java

## Purpose
Source file in package com.hierynomus.protocol.commons defining class ByteArrayUtils for the SMBJ user-network filesystem source tree.

## Important APIs / Types / Functions
Defines class `ByteArrayUtils` in package `com.hierynomus.protocol.commons`. Important methods/functions include `equals`, `printHex`, `toHex`, `parseHex`, `parseHexDigit`. Source size: 143 lines.

## Control Flow
Control flow is simple delegation through the package's interface or data holder contract.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Dependencies are limited to same-package language constructs and no explicit imports.

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction.

## Test Signals
Compile-time contract tests and focused unit tests around public methods are the primary signal.
