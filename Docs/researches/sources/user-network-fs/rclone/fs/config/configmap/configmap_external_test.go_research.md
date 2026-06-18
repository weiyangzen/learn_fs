# sources/user-network-fs/rclone/fs/config/configmap/configmap_external_test.go

Purpose: tests `configmap.Simple` string rendering from an external package and verifies the output round-trips through the public fspath parser.

Important APIs/functions: `TestSimpleString` covers machine string form with quoted values. `TestSimpleHuman` covers human-readable form with unquoted simple values and omitted `=true` booleans.

Control flow: each case renders a `Simple`, builds an inline remote string like `:local,<params>:`, parses it with `fspath.Parse`, and compares the parsed config map when applicable.

State and persistence behavior: no persistent state. The tests document stable sorted key order, quoting for special characters, and single-quote escaping.

Dependencies and integration points: depends on `configmap`, `fspath.Parse`, and `testify`. It protects compatibility between config map rendering and inline remote syntax.

Risks: tests intentionally assert exact strings, so formatting changes must be deliberate and parser-compatible.

Test signals: high signal for user-visible inline config representation and round-trip behavior.
