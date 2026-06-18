# sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/NtlmException.java

## Purpose
Runtime exception used to rethrow NTLM cryptographic or protocol failures without checked exception plumbing.

## Important APIs / Types / Functions
Defines class `NtlmException` in package `com.hierynomus.ntlm`. Important methods/functions include `NtlmException`. Source size: 37 lines.

## Control Flow
Control flow is NTLM message construction or parsing: security-buffer length/offset records are written first, payloads follow at computed offsets, and challenge parsing repositions the Buffer read cursor to offset-described target name and target-info payloads.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Dependencies are limited to same-package language constructs and no explicit imports.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Use MS-NLMP known-answer vectors for negotiate/challenge/authenticate bytes and NTLMv1/v2 hashes.
