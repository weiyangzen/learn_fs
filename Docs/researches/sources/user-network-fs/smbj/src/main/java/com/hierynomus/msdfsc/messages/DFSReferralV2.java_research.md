# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdfsc/messages/DFSReferralV2.java

Source read signal: reviewed complete local file (76 lines, 3102 bytes).

## Purpose
`DFSReferralV2.java` covers DFS referral version 2. parses V2 referral entries with fixed header size, TTL, path offsets, DFS path, alternate path, and network address path.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Reads offset fields relative to referral start and decodes UTF-16 strings after preserving/restoring buffer position; size is the fixed V2 structure plus string data on write.

## State and persistence
State is inherited path/DFS path/alternate path/TTL fields.

## Dependencies and integration points
Integrates with response parsing and referral cache target construction.

## Risks
Incorrect offset or size calculation corrupts subsequent referral entries. Null or illegal paths are rejected later by cache construction.

## Test signals
Signals are V2 referral parse/write tests and DFS link resolution.
