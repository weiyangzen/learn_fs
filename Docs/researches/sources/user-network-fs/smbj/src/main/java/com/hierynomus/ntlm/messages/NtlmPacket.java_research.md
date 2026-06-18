# sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/messages/NtlmPacket.java

## Purpose
Source file in package com.hierynomus.ntlm.messages defining class NtlmPacket for the SMBJ user-network filesystem source tree.

## Important APIs / Types / Functions
Defines class `NtlmPacket` in package `com.hierynomus.ntlm.messages`. Important methods/functions include `write`, `read`. Source size: 32 lines.

## Control Flow
Control flow is NTLM message construction or parsing: security-buffer length/offset records are written first, payloads follow at computed offsets, and challenge parsing repositions the Buffer read cursor to offset-described target name and target-info payloads.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.Packet, com.hierynomus.protocol.commons.buffer.Buffer.

## Risks and Edge Cases
some API surface intentionally throws unsupported/TODO behavior and callers need explicit coverage.

## Test Signals
Use MS-NLMP known-answer vectors for negotiate/challenge/authenticate bytes and NTLMv1/v2 hashes.
