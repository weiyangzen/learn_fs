# sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/messages/Utils.java

## Purpose
Source file in package com.hierynomus.ntlm.messages defining class Utils for the SMBJ user-network filesystem source tree.

## Important APIs / Types / Functions
Defines class `Utils` in package `com.hierynomus.ntlm.messages`. Important methods/functions include `Utils`, `writeOffsettedByteArrayFields`, `ensureNotNull`. Important fields include `EMPTY`. Source size: 46 lines.

## Control Flow
Control flow is NTLM message construction or parsing: security-buffer length/offset records are written first, payloads follow at computed offsets, and challenge parsing repositions the Buffer read cursor to offset-described target name and target-info payloads.

## State and Persistence
State fields observed: EMPTY. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.buffer.Buffer, com.hierynomus.ntlm.functions.NtlmFunctions.unicode.

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction.

## Test Signals
Use MS-NLMP known-answer vectors for negotiate/challenge/authenticate bytes and NTLMv1/v2 hashes.
