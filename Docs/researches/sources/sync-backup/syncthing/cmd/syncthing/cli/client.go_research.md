# sources/sync-backup/syncthing/cmd/syncthing/cli/client.go

Purpose: provides the REST API client used by `syncthing cli` subcommands.

Important APIs/types/functions: `APIClient`, `apiClient`, `apiClientFactory`, `getClient`, `loadGUIConfig`, `Endpoint`, `Do`, `Request`, `RequestString`, `RequestJSON`, `Get`, `Post`, `PutJSON`, `errNotFound`, and `checkResponse`.

Control flow: `getClient` either uses explicit GUI address/API key or loads local cert/config to discover GUI settings. It builds an HTTP client with a custom dialer that dials the configured GUI network/address and disables TLS verification for local GUI certs. Requests are built under `Endpoint()+"rest/"`, `X-Api-Key` is injected in `Do`, and `checkResponse` maps 404/401/non-200 statuses into errors with body text.

State and persistence: reads config and cert/key from Syncthing locations; no writes.

Dependencies/integration: depends on Syncthing config, locations, protocol device IDs, and standard HTTP/TLS.

Risks and test signals: `InsecureSkipVerify` is acceptable for local pinned API-key access but must not be treated as generic remote trust. `checkResponse` only treats HTTP 200 as success, so endpoints returning other 2xx codes would be flagged. No tests in this subset cover API client behavior.
