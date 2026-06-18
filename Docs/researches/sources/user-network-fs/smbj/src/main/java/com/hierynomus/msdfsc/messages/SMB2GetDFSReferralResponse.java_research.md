# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdfsc/messages/SMB2GetDFSReferralResponse.java

Source read signal: reviewed complete local file (117 lines, 4085 bytes).

## Purpose
`SMB2GetDFSReferralResponse.java` covers DFS referral response parser/writer. reads response header flags, referral count, consumed path length, and a list of referral entries; writes the same structure with entry data packed after headers.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Read loops over `numberOfReferrals`, dispatches `DFSReferral.factory()`, and fills missing `dfsPath` from the original path. Write computes the end of all entry headers, writes entries with data offsets, then writes offsetted data.

## State and persistence
State is original path, path consumed, header flags, and mutable referral entry list.

## Dependencies and integration points
Integrates with referral cache construction, domain cache construction, and DFS client path resolution.

## Risks
No explicit validation of count vs buffer length beyond buffer exceptions. Mixed-version referral lists depend on first-entry version for callers.

## Test signals
Signals are response parse/write roundtrips and DFS integration tests.
