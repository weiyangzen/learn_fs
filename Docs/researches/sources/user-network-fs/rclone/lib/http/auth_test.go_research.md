# sources/user-network-fs/rclone/lib/http/auth_test.go

Source read signal: reviewed complete local file (15 lines, sha256 3a398323fd657357).

Purpose: Verifies that authentication help text uses the requested flag prefix.

Important APIs/types/functions: `TestHelpPrefixAuth` calls `AuthHelp`.

Control flow: The test renders help with a sentinel prefix and fails if the prefix is absent.

State and persistence behavior: Stateless.

Dependencies and integration points: Uses `strings` and `testing`; protects template interpolation in CLI help.

Risks and test signals: This is a light smoke test and does not validate every documented option or wording.
