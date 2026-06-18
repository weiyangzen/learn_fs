# sources/user-network-fs/rclone/cmd/bisync/log.go

Purpose: Centralizes bisync-specific logging formatting, path escaping, optional terminal colors, OS path encoding, and JSON pretty-print debugging.

Important APIs/types/functions: `indentf` and `indent` emit aligned Path1/Path2 action logs. `escapePath` and `quotePath` encode and quote paths safely. `Colors`, `ColorsLock`, `Color`, and `ColorX` gate terminal color sequences. `encode` round-trips paths through rclone's OS encoder. `prettyprint` JSON-formats arbitrary debug/info structures.

Control flow: `indent` chooses log severity based on tags: `ERROR` uses `fs.Errorf`, `INFO` removes the tag, `!` prefixes force notice-level `fs.Logf`, and dry-run upgrades output visibility to log level. It colorizes path, tag, and message fragments and highlights queue copy/delete text. Path escaping quotes only when control characters or forced quotes require it, with Windows backslashes normalized for quote testing.

State and persistence behavior: No direct persistence. Global color state is protected by a mutex and is enabled by `Bisync` or tests when terminal color mode allows it. Logs are consumed by CLI, RC capture, and golden tests.

Dependencies and integration points: Used throughout bisync for user-facing decisions and debug dumps. Integrates with rclone fs logging, terminal styles, and encoder path conversions.

Risks: Log text is part of golden test expectations and user diagnostics, so wording/spacing changes have broad test impact. `ColorX` currently duplicates `Color`. `prettyprint` logs empty bytes if marshal fails after debuging the marshal error.

Test signals: Golden log comparison in `bisync_test.go` heavily exercises this. Path escaping is indirectly tested by extended filename/path scenarios and Windows slash normalization rules.
