# sources/object-store/minio-mc/cmd/diff-main.go

Purpose: Implements `mc diff`, a directory/bucket comparison command.

Important APIs/types/functions: `diffCmd`, `diffMessage`, `String`, `JSON`, `checkDiffSyntax`, `doDiffMain`, and `mainDiff`.

Control flow: `mainDiff` parses encryption flags, validates two directory-like arguments, sets output colors, and calls `doDiffMain`. `doDiffMain` normalizes trailing separators, expands aliases, builds clients, then prints messages from `bucketObjectDifference`.

State and persistence: Read-only against source and target listings; no local persistence.

Dependencies/integration: Uses encryption key parsing, `url2Stat`, `newClientFromAlias`, `bucketObjectDifference`, global context, and console/json output.

Risks: The command compares names, size, type, and certain metadata, not object bytes. Missing destination can be accepted during syntax validation only for specific object-missing errors.

Test signals: No direct command tests; `difference_test.go` covers an exclude helper used by related comparison/mirror code.
