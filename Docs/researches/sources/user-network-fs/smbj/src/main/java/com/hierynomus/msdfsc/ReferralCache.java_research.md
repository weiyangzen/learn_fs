# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdfsc/ReferralCache.java

Source read signal: reviewed complete local file (262 lines, 11320 bytes).

## Purpose
`ReferralCache.java` covers DFS referral cache tree. stores DFS root/link/sysvol referral responses in a concurrent prefix tree with TTL, target hinting, interlink detection, and clear operations.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
`put()` splits the DFS path prefix into nodes; `lookup()` walks as far as possible and returns the nearest entry; `clear()` removes expired non-root entries under a path; entries are built from `SMB2GetDFSReferralResponse` and `DomainCache`.

## State and persistence
State is an in-memory tree of `ReferralCacheNode` objects with volatile atomic entry updates, target hint index, immutable target list, and computed expiry time.

## Dependencies and integration points
Integrates DFS referral response classes, `DFSPath`, domain cache, and SMB path resolution/fallback.

## Risks
Concurrent node insertion uses get/put rather than `computeIfAbsent`, so duplicate temporary nodes can be created. `clear()` on an expired entry clears child nodes too. TTL uses wall-clock milliseconds.

## Test signals
Signals are DFS cache unit tests, target fallback behavior, and DFS integration tests using broken-first links.
