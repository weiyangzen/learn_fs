# File Research: sources/os/plan9/plan9/sys/src/cmd/cifs/dfs.c

DFS referral and path remapping layer. Maintains a linked `Dfscache` from client-visible source path to target host/share/path, with expiry, proximity, and RTT. `mapfile` converts Plan 9 path to current target path; `mapshare` resolves or autoconnects the target share, trying both normal and `$` hidden variants.

`redirect` obtains referrals via `T2getdfsreferral`, recursively follows non-storage referrals, pings candidate hosts, and chooses a target based on proximity plus RTT tolerance. The comments document deliberate limitations: it does not spawn separate CIFS client instances for other servers, relies on NetBIOS-style hostnames, and treats many DFS/AD behaviors empirically.
