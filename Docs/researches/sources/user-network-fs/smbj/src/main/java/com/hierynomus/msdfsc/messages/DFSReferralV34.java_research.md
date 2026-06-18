# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdfsc/messages/DFSReferralV34.java

Source read signal: reviewed complete local file (119 lines, 5244 bytes).

## Purpose
`DFSReferralV34.java` covers DFS referral versions 3 and 4. handles modern referrals including path offsets, special names, expanded-name lists, TTL, and V4 target-set boundary flags.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Reads the fixed V3/V4 body, decodes DFS/network/special strings, reads expanded names when `NameListReferral` is set, and writes offsetted string data after entry headers.

## State and persistence
State includes inherited referral fields plus expanded names and target-set-boundary flag exposure through entry flags.

## Dependencies and integration points
Integrates with domain cache, referral cache, DFS response writing, and `EnumWithValue` flag checks.

## Risks
Expanded-name parsing depends on count and null termination. V3/V4 share code but V4-only semantics such as target-set boundary can be easy to lose.

## Test signals
Signals are DC referral tests, V3/V4 binary fixture roundtrips, and DFS domain/interlink tests.
