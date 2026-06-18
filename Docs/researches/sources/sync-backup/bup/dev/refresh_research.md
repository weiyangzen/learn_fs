# sources/sync-backup/bup/dev/refresh

## Purpose
Sponge-like helper that updates a destination file only when content changes, optionally appending and optionally reporting refreshes.

## Important APIs, Types, and Functions
Options are `-a`, `-v`, optional `--`, and `DEST`. Uses `mktemp`, `cp -Lp`, `cmp -s`, and `mv`.

## Control Flow
Copies existing destination permissions/content to a temp file if present, writes stdin by replace or append mode, compares temp with destination, and atomically moves temp into place only on content change.

## State and Persistence Behavior
Creates a temporary sibling file and may replace destination. Trap removes temp on exit.

## Dependencies and Integration Points
Used by `configure`, `update-checkout-info`, and generated docs/config workflows to avoid unnecessary rebuilds.

## Risks and Test Signals
Risks are temp filename creation next to nonexistent/permission-denied dest and symlink behavior via `cp -Lp`. Signals are unchanged mtime/content when equal and updated file when different.
