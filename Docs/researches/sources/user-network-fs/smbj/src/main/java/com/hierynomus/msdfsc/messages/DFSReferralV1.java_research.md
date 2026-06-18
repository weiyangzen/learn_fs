# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdfsc/messages/DFSReferralV1.java

Source read signal: reviewed complete local file (54 lines, 1696 bytes).

## Purpose
`DFSReferralV1.java` covers DFS referral version 1. implements legacy V1 referral parsing/writing, mainly reading a UTF-16 network address path after TTL.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Reads V1-specific fields from `SMBBuffer`, decodes null-terminated strings, and reports its computed size.

## State and persistence
State is inherited referral fields such as path and TTL.

## Dependencies and integration points
Integrates through `DFSReferral.factory()`.

## Risks
V1 has fewer offsets than later versions, so common cache code must handle missing DFS path fields.

## Test signals
Signals are V1 referral binary fixtures and fallback to original path when needed.
