# sources/user-network-fs/samba/source3/include/msdfs.h

## Purpose
`msdfs.h` defines constants and record layouts for Microsoft DFS referrals served by Samba. It describes referral TTLs, reply flags and sizes, referral list limits, and in-memory maps from DFS junctions to alternate targets.

## Important APIs, Types, And Control Flow
Constants include `REFERRAL_TTL`, referral-server/storage-server flags, version 2 and version 3 referral record sizes, referral header size, and maximum referral and junction counts. `struct client_dfs_referral` describes a referral returned to a client with proximity, TTL, and DFS path. `struct referral` stores alternate target path, proximity, and TTL. `struct junction_map` groups a service/volume/comment with a referral count and referral list.

## State And Persistence
The header has no active state, but its structures model configured DFS junction state and transient referral responses. TTL values control client-side caching, while max counts bound memory and protocol response construction.

## Dependencies And Integration Points
It integrates with trans2/SMB DFS referral reply construction, share/path resolution, DFS junction management, and clients following referrals across servers. The structures depend on Samba allocation and string ownership conventions even though this header does not declare functions.

## Risks And Test Signals
Risks include referral count overflow, invalid target path ownership, TTL changes causing stale referrals or excessive refreshes, and version-specific size mismatches in wire replies. Test signals include version 2 and 3 referral encoding, max referral count rejection, junction lookup for multiple targets, client cache TTL behavior, storage-server flag correctness, and path normalization for DFS targets.
