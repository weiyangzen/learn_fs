# File Research: sources/os/plan9/9front/sys/src/cmd/cifs/dfs.c

Implements DFS referral caching and path/share remapping for the CIFS 9P server. The introductory comment documents pragmatic limitations: no AD/Kerberos/LDAP DNS referral lookup, reliance on NetBIOS names matching DNS hostnames, no spawning additional CIFS instances for other DFS servers, and special behavior around DFS reparse points.

Maintains a linked `Dfscache` table mapping source paths to selected target host/share/path with expiry and measured RTT. `dfscacheinfo` renders this cache for the synthetic info filesystem.

`mapfile` rewrites a Plan 9 path into the target share-relative CIFS path. `mapshare` maps a path to an existing connected share or auto-connects to the referred share, trying both plain and `$` hidden-share variants.

`redirect` is the main entry point for resolving or refreshing DFS referrals. It uses `T2getdfsreferral`, recursively follows non-storage referral levels via `redir1`, pings candidate targets, and chooses usable mappings with a tolerance that biases toward earlier Active Directory referral ordering.

Important dependencies: `T2getdfsreferral` from `trans2.c`, `CIFStreeconnect`, `ping`, global `Shares/Nshares/Sess`, and `Checkcase/Debug/Dfstout`.

Risk notes: cache mutation is global and not visibly synchronized; case checking has a `Badmatch` enum but lookup only sets exact/no match; behavior is heavily based on observed Windows/Samba quirks rather than a complete DFS/AD implementation.
