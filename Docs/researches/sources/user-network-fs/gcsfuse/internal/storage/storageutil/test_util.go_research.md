## sources/user-network-fs/gcsfuse/internal/storage/storageutil/test_util.go

Purpose: Supplies shared storage client test defaults and constants.

Important APIs/types/functions: `CustomEndpoint`, `CustomTokenUrl`, and `GetDefaultStorageClientConfig(keyFile)` returning a populated `StorageClientConfig`.

Control flow: constructs an HTTP/1 config with retry, timeout, user-agent, auth, HNS, read-stall retry defaults, and empty write config.

State and persistence behavior: no state; returns a new config value.

Dependencies and integration points: used heavily by storageutil and storage handle tests to reduce setup duplication and keep test defaults aligned with production config shape.

Risks: if production defaults change but this helper does not, tests may validate stale assumptions. User-agent string is fixed to a test build signature.

Test signals: not directly tested; its correctness is exercised by many dependent tests.
