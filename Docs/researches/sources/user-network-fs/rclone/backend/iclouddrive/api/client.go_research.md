<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/iclouddrive/api/client.go -->
## Research: sources/user-network-fs/rclone/backend/iclouddrive/api/client.go

### Purpose
`client.go` defines the top-level iCloud API client used by both Drive and Photos services. It owns credentials, the mutable `Session`, a REST client, a service-specific PCS-cookie scope, optional session persistence callback, and lazy construction of `DriveService`. It centralizes authentication reuse, reauthentication on expired sessions, and disk caching of Apple webservice endpoint metadata.

### Important APIs, Types, and Functions
The exported constants define Apple endpoints (`baseEndpoint`, `setupEndpoint`, `authEndpoint`) and account webservice keys (`WsDrive`, `WsDocs`, `WsPhotos`). `Client` stores the lowercased Apple ID, password, remote cache namespace, PCS webservice key, REST client, `Session`, callback, cached `DriveService`, and mutex. `New` creates a client and seeds trust token, cookies, and client ID into a fresh `Session`.

`DriveService` lazily calls `NewDriveService`. `Request` wraps `Session.Request` and reauthenticates on status 401, 421, or 423 before retrying once. `Authenticate` serializes auth with the client mutex, calls `authenticateSession`, then ensures ADP/PCS cookies for the configured service. `IntoReader` JSON-marshals request bodies. `RequestError` represents successful HTTP responses that contain a failing iCloud inner status.

### Control Flow
Authentication uses the cheapest valid path first. If saved cookies and `AccountInfo.Webservices` exist, validation is skipped and requests fail lazily if the session is bad. If cookies exist without in-memory endpoints, `loadCachedWebservices` tries `webservices.json`. If still needed, `ValidateSession` is attempted. On failure, cookies are cleared and a full SRP sign-in is started through `Session.SignIn`; if 2FA is required, the caller must continue the interactive config flow. Otherwise `AuthWithToken` finalizes the account session and webservice endpoints are cached.

### State and Persistence
The stateful pieces are `Session` fields, saved cookies/trust token handled by callers, and `webservices.json` under `config.GetCacheDir()/iclouddrive-photos/<remoteName>/`. The remote name is sanitized with `filepath.Base` for cache namespacing. `ClearCacheDir` removes all cached files for a remote. The session callback is invoked after a successful full auth and after new PCS cookies are acquired.

### Dependencies and Integration Points
This file uses rclone `fs`, `config`, `fshttp`, and `rest` packages. It integrates directly with `Session` from `session.go`, `DriveService` from `drive.go`, and shared cache helpers from `photos.go` (`cacheSubdir`, `saveJSONCache`). Photos code constructs `Client` with `pcsWSKey=WsPhotos`; Drive uses `WsDrive`.

### Risks and Edge Cases
Skipping validation when cookies and endpoints are present improves startup time but moves stale-session failures to first request. Reauth under `Request` returns `trust token expired, please reauth` when Apple demands 2FA. `loadCachedWebservices` trusts unexpired disk endpoint metadata if JSON parses and is non-empty; service URL changes or stale cache can cause later request failures. The client mutex protects auth and drive-service initialization but not all direct session field reads elsewhere.

### Test Signals
There is no direct `client.go` unit test in this subset. Behavior is indirectly tested through session tests, Photos HTTP tests that instantiate `Client`/`Session`, and backend config flows in `icloud.go`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/iclouddrive/api/client.go -->
