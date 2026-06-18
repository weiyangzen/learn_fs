# sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/functions/ComputedNtlmV2Response.java

## Purpose
Simple result carrier for the NTLMv2 NT response, LM response, and session base key computed from a challenge.

## Important APIs / Types / Functions
Defines class `ComputedNtlmV2Response` in package `com.hierynomus.ntlm.functions`. Important methods/functions include `ComputedNtlmV2Response`, `getNtResponse`, `getLmResponse`, `getSessionBaseKey`. Important fields include `ntResponse`, `lmResponse`, `sessionBaseKey`. Source size: 40 lines.

## Control Flow
Control flow is simple delegation through the package's interface or data holder contract.

## State and Persistence
State fields observed: ntResponse, lmResponse, sessionBaseKey. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Dependencies are limited to same-package language constructs and no explicit imports.

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction.

## Test Signals
Use MS-NLMP known-answer vectors for negotiate/challenge/authenticate bytes and NTLMv1/v2 hashes.
