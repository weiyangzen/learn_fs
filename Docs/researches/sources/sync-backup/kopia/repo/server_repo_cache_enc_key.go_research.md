# sources/sync-backup/kopia/repo/server_repo_cache_enc_key.go

Purpose: defines supported key-derivation algorithms for encrypting local content cache used by API-server repository connections.

Important APIs/types/functions: `DefaultServerRepoCacheKeyDerivationAlgorithm` is `crypto.ScryptAlgorithm`. `SupportedLocalCacheKeyDerivationAlgorithms` returns scrypt and PBKDF2 algorithm names.

Control flow: no branching beyond returning the supported slice. `open.go` uses the default when server info omits an algorithm.

State and persistence behavior: no local state. The selected algorithm affects persistent cache encryption compatibility.

Dependencies/integration: depends on `internal/crypto` algorithm constants and is consumed by API server connection/cache code.

Risks: changing defaults or supported algorithms can make existing encrypted caches unreadable or alter connection performance/security properties. The returned slice is newly allocated by literal, so callers can mutate it without changing globals.

Test signals: indirectly covered by API server repository open tests; no direct unit test here.
