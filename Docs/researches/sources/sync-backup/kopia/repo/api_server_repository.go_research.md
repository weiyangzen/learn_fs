# sources/sync-backup/kopia/repo/api_server_repository.go

Purpose: persists local configuration for connecting to a remote Kopia API server and verifies the connection.

Important APIs/types/functions: `APIServerInfo` and `ConnectAPIServer`. `APIServerInfo` stores base URL, trusted server certificate fingerprint, and local cache key-derivation algorithm.

Control flow: `ConnectAPIServer` builds a `LocalConfig` with API server info and client options after applying defaults labeled with the API server URL. It calls `setupCachingOptionsWithDefaults` using the config path, caching options, and API base URL as cache identity input. It writes the local config to disk, then calls `verifyConnect` with the config file and password.

State and persistence behavior: this file writes the local repository configuration file. The struct comment explicitly notes backward compatibility because the JSON may be read/written by different Kopia versions.

Dependencies/integration points: integrates with repository connect options, local config writing, cache setup, and connection verification. Risks include partial configuration write failures preventing verification, persistent schema compatibility constraints, and reliance on URL bytes for cache derivation uniqueness. Test signals are outside this subset; no direct tests are included here.
