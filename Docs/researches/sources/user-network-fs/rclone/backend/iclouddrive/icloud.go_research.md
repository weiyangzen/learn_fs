<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/iclouddrive/icloud.go -->
## Research: sources/user-network-fs/rclone/backend/iclouddrive/icloud.go

### Purpose
`icloud.go` is the rclone registration and configuration entry point for the combined iCloud Drive and Photos backend. It registers the `iclouddrive` remote, exposes a `service` option that routes to Drive or Photos, drives the interactive SRP/2FA/SMS config state machine, persists auth credentials, creates authenticated API clients, and clears auth/cache state on disconnect.

### Important APIs, Types, and Functions
Constants define `configAuthSession`, `configService`, `serviceDrive`, and `servicePhotos`. `configAuthState` and `smsPhone` represent temporary auth state that must survive multi-step config prompts. Helpers include `saveAuthSession`, `loadAuthSession`, `restoreAuthSession`, `resumeConfigClient`, `saveAuthCredentials`, `triggerSMSFlow`, `newICloudClient`, `disconnectClient`, and `NewServiceFs`. `Config` is the main rclone config state machine. `init` registers backend metadata, options, and read-only Photos metadata keys (`width`, `height`, `added-time`, `favorite`, `hidden`).

### Control Flow
On initial config, `Config` requires Apple ID, reveals the obscured password, ignores stale trust token/cookies, creates a fresh API client, and calls `Authenticate`. If Apple requires 2FA, it fetches auth state. Accounts without trusted devices but with trusted phone numbers are sent into SMS flow. Otherwise it explicitly requests a trusted-device push, stores auth session state, and prompts for a 2FA code or `sms`.

In `2fa_do`, the saved session is restored to avoid another SRP round trip. A literal `sms` branches to phone selection or SMS trigger; otherwise the code is validated via trusted-device flow and credentials are saved. `2fa_sms_select` parses the selected `ID_mode`, requests the SMS code, saves state, and prompts for the code. `2fa_sms_*` validates the SMS code, trusts the session, saves trust token/cookies, clears temporary state, and clears cache.

### State and Persistence
Temporary auth session state is JSON-marshaled, base64-encoded, and stored in config key `_auth_session`. Long-lived credentials are `configTrustToken` and `configCookies`. `saveAuthCredentials` clears `_auth_session` and removes the remote cache through `api.ClearCacheDir`. `newICloudClient` installs a callback that persists updated cookies when the API session changes. `disconnectClient` clears trust token, cookies, auth-session state, and deletes the API cache dir.

### Dependencies and Integration Points
This file integrates rclone `fs.Register`, `configmap`, `configstruct`, `obscure`, `encoder`, and the iCloud API package. `NewServiceFs` routes to `NewFs` for Drive and `NewFsPhotos` for Photos, both defined elsewhere in the backend. It scopes PCS cookie acquisition through `newICloudClient` by passing `WsDrive` or `WsPhotos` from the service-specific constructors.

### Risks and Edge Cases
The config flow relies on Apple private auth behavior and may need updates when Apple changes 2FA push semantics; comments note iOS 26.4+ requiring explicit push notification. Losing `_auth_session` between config steps forces reconfiguration. SMS state encodes phone ID/mode in the state string and must parse cleanly. Fresh config intentionally ignores old trust tokens/cookies to force reauthentication, while normal backend creation requires a trust token and returns a reconnect hint if missing.

### Test Signals
No direct tests for `icloud.go` are in this subset. Its behavior is indirectly protected by `session.go`/`session_test.go` for cookie/auth primitives and by service-specific backend tests elsewhere.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/iclouddrive/icloud.go -->
