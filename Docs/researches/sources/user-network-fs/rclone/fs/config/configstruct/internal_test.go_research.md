# sources/user-network-fs/rclone/fs/config/configstruct/internal_test.go

Purpose: tests the unexported `camelToSnake` helper inside the `configstruct` package.

Important APIs/functions: `TestCamelToSnake` covers empty string, simple field names, normal CamelCase, and all-caps initialisms such as `AccessKeyID`.

Control flow: table-driven pure function assertions compare generated config names.

State and persistence behavior: none. The helper determines default config key names when struct fields lack tags.

Dependencies and integration points: uses `testify/assert`. It protects naming used by `Items`, `Set`, and `SetAny`.

Risks: the regex strategy inserts underscores before uppercase runs; tests cover common initialism behavior but not every acronym pattern.

Test signals: focused coverage for a key naming primitive.
