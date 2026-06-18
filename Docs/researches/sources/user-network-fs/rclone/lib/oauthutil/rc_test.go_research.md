# sources/user-network-fs/rclone/lib/oauthutil/rc_test.go

Source read signal: reviewed complete local file (68 lines, sha256 b9ed33edb63ebcb9).

Purpose: Tests remote-control endpoints that report or stop an active OAuth flow.

Important APIs/types/functions: `TestRcOAuthStatus` and `TestRcOAuthStop`.

Control flow: Tests fetch registered rc calls, assert stopped status/error with no active flow, manually install `oauthCancelFn` and `oauthURL` under lock, then verify running status, auth URL reporting, successful stop, and repeated-stop error.

State and persistence behavior: Mutates package globals `oauthCancelFn` and `oauthURL`, restoring them with deferred cleanup.

Dependencies and integration points: Uses `rc.Calls`, `context`, `testify/assert`, and `require`. Validates `init` rc registration in `oauthutil.go`.

Risks and test signals: Covers only rc state management, not the real auth server or cancellation during `configSetup`.
