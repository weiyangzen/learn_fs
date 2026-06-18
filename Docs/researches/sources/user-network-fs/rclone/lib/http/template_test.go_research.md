# sources/user-network-fs/rclone/lib/http/template_test.go

Source read signal: reviewed complete local file (15 lines, sha256 667802e96bc03f7a).

Purpose: Smoke-tests template help prefix interpolation.

Important APIs/types/functions: `TestHelpPrefixTemplate` calls `TemplateHelp`.

Control flow: Renders help with a sentinel prefix and asserts the prefix is present.

State and persistence behavior: Stateless.

Dependencies and integration points: Uses `strings` and `testing`.

Risks and test signals: Light coverage only; parsing and rendering behavior is covered indirectly by serve directory tests.
