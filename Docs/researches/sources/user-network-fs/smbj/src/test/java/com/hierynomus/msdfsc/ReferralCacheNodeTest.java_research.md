# sources/user-network-fs/smbj/src/test/java/com/hierynomus/msdfsc/ReferralCacheNodeTest.java
# sources/user-network-fs/smbj/src/test/java/com/hierynomus/msdfsc/ReferralCacheNodeTest.java

Purpose: tests DFS referral cache node behavior. It validates adding child referral nodes, resolving matching paths, choosing target referrals, and cache-tree traversal semantics for DFS roots and links.

State and persistence: in-memory referral cache tree only; no persistence. Dependencies include DFS path/referral/cache types and JUnit. Integration point is `DFSPathResolver` caching of referral responses to avoid repeated network IOCTLs. Risks covered include prefix matching, parent/child lookup, stale or wrong referral target selection, and path normalization. Test signal is important for DFS cache correctness but isolated from live SMB sessions.
