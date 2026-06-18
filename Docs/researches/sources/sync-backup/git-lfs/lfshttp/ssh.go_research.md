# sources/sync-backup/git-lfs/lfshttp/ssh.go

Purpose: Resolves SSH-based LFS authentication into HTTPS href/header data and optionally caches responses.

Important APIs/types/functions: `SSHResolver`, `withSSHCache`, `sshCache`, `sshCache.Resolve`, `sshAuthResponse`, `IsExpiredWithin`, `sshAuthClient`, and `sshAuthClient.Resolve`.

Control flow: Cache lookup keys by user/host, port, path, and method. Non-expired entries are returned; expired/missing entries delegate to the wrapped resolver. The concrete resolver executes `git-lfs-authenticate`, captures stdout/stderr, decodes JSON on success, stores creation time, and applies default token TTL if no expiry is provided.

State and persistence behavior: `sshCache` uses `sync.Map` for in-process cache. External SSH command execution may consult user SSH/config state. No files written here.

Dependencies and integration points: Used by `Client.NewRequest` through `sshResolveWithRetries`. Depends on `ssh.GetLFSExeAndArgs`, `subprocess.ExecCommand`, `tools.IsExpiredAtOrIn`, Git env, and tracer logging.

Risks and edge cases: Cache only stores successful resolutions. Expiration considers a five-second safety window in caller. Ambiguous expiry fields defer to helper semantics. Command stderr becomes `Message` for wrapped errors.

Test signals: `ssh_test.go` covers cache hits, expiry by `expires_at` and `expires_in`, concurrent resolves under race detector, and error non-caching.
