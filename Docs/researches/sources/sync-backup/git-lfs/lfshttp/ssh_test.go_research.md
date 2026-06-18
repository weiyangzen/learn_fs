# sources/sync-backup/git-lfs/lfshttp/ssh_test.go

Purpose: Tests SSH auth cache behavior, expiry semantics, error handling, and concurrent access.

Important APIs/types/functions: Exercises `withSSHCache`, `sshCache.Resolve`, `sshAuthResponse.IsExpiredWithin`, fake `SSHResolver`, and `sync.Map` cache storage.

Control flow: Tests seed cache entries or fake resolver responses, call `Resolve`, and assert whether cached or real response is returned. Concurrency test starts two goroutines resolving the same endpoint.

State and persistence behavior: Cache state is in memory. Fake resolver stores responses in a map, while cache stores successful responses in `sync.Map`.

Dependencies and integration points: Validates `ssh.SSHMetadata` keying and shared `errors` wrapping for failed fake resolution.

Risks and edge cases: Covers expired entries being bypassed but not deleted. Ambiguous expiration with future `expires_in` and past `expires_at` still returns cache.

Test signals: Good race-safety signal for cache map access. It does not run real `git-lfs-authenticate`.
