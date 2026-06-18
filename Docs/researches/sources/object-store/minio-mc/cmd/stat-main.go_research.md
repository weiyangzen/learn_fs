# sources/object-store/minio-mc/cmd/stat-main.go

## Purpose
Implements CLI registration and argument parsing for `mc stat`, which displays object, version, prefix, or bucket metadata.

## Important APIs, types, and functions
- `statFlags` defines `--rewind`, `--versions`, `--version-id`, `--recursive`, `--verbose`, and `--no-list`.
- `statCmd` registers the command with encryption-key support.
- `parseAndCheckStatSyntax` validates arguments, flag conflicts, and expands verbose alias-only targets to buckets.
- `mainStat` configures output colors, parses encryption keys, validates args, and calls `statURL` for each target.

## Control flow
Parsing requires non-empty arguments, rejects empty strings, rejects `--version-id` with multiple targets or with recursive/version/rewind flags, and rejects `--no-list` with recursive/version modes. In verbose mode for alias-only targets, it lists buckets and expands the target list to each bucket when possible.

`mainStat` sets object and bucket color themes, validates encryption keys, obtains parsed targets and mode flags, then calls `statURL` with `headOnly` from `--no-list`.

## State and persistence
Read-only. It does not persist local or remote state.

## Dependencies and integration points
Uses `stat.go` for actual metadata retrieval/formatting, encryption-key parsing, `newClient`, `ListBuckets`, global output/fatal helpers, and CLI/global flags.

## Risks and edge cases
- Verbose alias expansion depends on `ListBuckets`; if it fails or returns none, the original alias target is kept.
- `--no-list` is a direct HEAD path and intentionally incompatible with list-based modes.
- The fallback `args = []string{"."}` is unreachable after current syntax validation but preserves old behavior shape.

## Test signals
No direct tests for this file. Tests should cover flag conflict validation and verbose alias bucket expansion.
