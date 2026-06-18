# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdfsc/DomainCache.java

Source read signal: reviewed complete local file (99 lines, 4982 bytes).

## Purpose
`DomainCache.java` covers DFS domain referral cache. stores trusted domain referral data keyed by domain name, with DC hint and DC list parsed from DFS referral responses.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
A `DomainCacheEntry` validates one referral, requires `NameListReferral`, reads `specialName` as domain and expanded names as DCs, then `put()` stores it in a concurrent map.

## State and persistence
State is an in-memory `ConcurrentHashMap` with no TTL handling in this class.

## Dependencies and integration points
Integrates with DFS referral parsing and `ReferralCache` interlink detection.

## Risks
Lookup is case-sensitive and there is no expiration/refresh. Empty expanded-name lists would fail when selecting the first DC.

## Test signals
Signals are DFS referral parsing tests and interlink detection tests.
