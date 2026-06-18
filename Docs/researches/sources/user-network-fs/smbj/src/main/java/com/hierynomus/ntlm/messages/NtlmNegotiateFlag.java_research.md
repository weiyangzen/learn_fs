# sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/messages/NtlmNegotiateFlag.java

## Purpose
Source file in package com.hierynomus.ntlm.messages defining enum NtlmNegotiateFlag for the SMBJ user-network filesystem source tree.

## Important APIs / Types / Functions
Defines enum `NtlmNegotiateFlag` in package `com.hierynomus.ntlm.messages`. Important methods/functions include `NtlmNegotiateFlag`, `getValue`. Important fields include `value`. Source size: 60 lines.

## Control Flow
Control flow is NTLM message construction or parsing: security-buffer length/offset records are written first, payloads follow at computed offsets, and challenge parsing repositions the Buffer read cursor to offset-described target name and target-info payloads.

## State and Persistence
State fields observed: value. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.EnumWithValue.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Use MS-NLMP known-answer vectors for negotiate/challenge/authenticate bytes and NTLMv1/v2 hashes.
