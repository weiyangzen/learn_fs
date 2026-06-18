# sources/user-network-fs/rclone/backend/seafile/seafile_internal_test.go

Purpose: unit tests private Seafile backend path and configuration behavior that does not require a live Seafile server.

Important APIs/types/functions: `pathData` defines cases for `Fs.splitPath`, combining configured library, configured root, command argument path, and expected library/path output. `TestSplitPath` instantiates minimal `Fs` values and verifies path decomposition. `TestSplitPathIntoSlice` covers the package-level `splitPath` helper used by recursive directory creation. `Test2FAStateMachine` exercises `Config` with `configmap.Simple` and `fs.ConfigIn`.

Control flow: `TestSplitPath` enumerates unrooted and library-rooted remotes, including empty roots, single library names, nested file paths, and configured root prefixes. The 2FA test drives `Config` through initial state, password prompting, password validation, 2FA prompt, blank-code retry, explicit retry after failure, and terminal failure. It does not mock a successful token exchange, so network-dependent `2fa_do` success is intentionally absent.

State and persistence behavior: tests assert mapper mutation indirectly for password entry by following the next state, and use obscured config password for the "ready for token" path. They verify that no output is returned when 2FA is disabled.

Dependencies/integration: uses rclone `fs.ConfigIn`, `configmap.Simple`, `obscure`, and `testify` assertions. It targets private functions in package `seafile`, not external package tests.

Risks/test signals: good coverage for path-root semantics and the interactive 2FA state machine. Missing signals include successful 2FA token persistence, HTTP token failure variants, library cache behavior, encrypted-library authorization, and Seafile object operations.
