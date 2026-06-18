# sources/sync-backup/kopia/repo/userhost.go

Purpose: derives default username and hostname for repository client options and source labels.

Important APIs/types/functions: `GetDefaultUserName(ctx)` reads `os/user.Current`, logs and returns `"nobody"` on error, and strips Windows domain prefixes. `GetDefaultHostName(ctx)` reads `os.Hostname`, logs and returns `"nohost"` on error, lowercases and truncates at the first dot.

Control flow: both functions are fallback-safe and log errors through the repo logger. Hostname normalization reduces FQDNs to short lowercase hosts.

State and persistence behavior: no direct persistence, but returned values are stored in client options, session metadata, snapshot labels, and policy labels.

Dependencies/integration: uses standard `os`, `os/user`, `runtime`, `strings`, and package logger.

Risks: username/hostname normalization affects snapshot source identity; changes can split or merge policy/snapshot histories. Windows domain stripping assumes backslash separator.

Test signals: no direct tests in this subset.
