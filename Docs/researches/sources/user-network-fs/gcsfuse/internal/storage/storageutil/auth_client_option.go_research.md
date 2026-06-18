## sources/user-network-fs/gcsfuse/internal/storage/storageutil/auth_client_option.go

Purpose: Builds Google API client auth options and an OAuth2 token source for storage clients, supporting token URL credentials, key-file credentials, ADC, universe-domain discovery, and a quota-project workaround.

Important APIs/types/functions: `GetClientAuthOptionsAndToken(ctx, config)` returns `[]option.ClientOption`, `oauth2.TokenSource`, and error. It uses `auth2.NewTokenSourceFromURL`, `auth2.GetCredentials`, `oauth2adapt.TokenSourceFromTokenProvider`, `cred.UniverseDomain`, `NewRetryConfig`, and `ExecuteWithRetryAtLogLevel`.

Control flow: token URL takes precedence and produces only `option.WithTokenSource`. Otherwise credentials are loaded, converted to token source, and a universe domain is chosen. Standard ADC on commercial GCP bypasses metadata lookup; other cases retry `cred.UniverseDomain` and fall back to `googleapis.com` on failure. Final options include universe domain plus `option.WithAuthCredentials` using a reconstructed credentials object.

State and persistence behavior: reads environment `GOOGLE_CLOUD_UNIVERSE_DOMAIN` and may contact credential providers or metadata services through auth libraries. It logs universe-domain decisions but does not persist state.

Dependencies and integration points: used by HTTP/gRPC storage client creation when Google library auth is enabled. Tightly coupled to `StorageClientConfig`, internal auth package constants, retry helper defaults, and Google API option semantics.

Risks: fallback to default universe domain can mask auth environment problems. Token URL path returns fewer options than key/ADC path. The TODO workaround intentionally drops quota project ID until an upstream auth issue is resolved, so future auth-library upgrades must revisit this file.

Test signals: `auth_client_option_test.go` covers token URL success/error and key-file fallback success/error, including expected client option counts.
