# sources/object-store/minio-mc/cmd/rm-main.go

## Purpose
Implements `mc rm`, including single-object deletion, recursive deletion, versioned deletion, incomplete upload deletion, dry-run, stdin-driven deletion, retention governance bypass, non-current version cleanup, dangerous namespace removal protection, and hidden purge behavior.

## Important APIs, types, and functions
- `rmFlags` defines deletion mode, safety, version, rewind, incomplete upload, dry-run, stdin, age filters, bypass, non-current, and hidden purge flags.
- `rmCmd` registers the command.
- `rmMessage` is the output model for removed objects, delete markers, versions, mod time, and dry-run.
- `checkRmSyntax` enforces safety and incompatible flag combinations.
- `removeSingle` handles direct deletion of one object or one version.
- `removeOpts` carries deletion behavior into helpers.
- `printDryRunMsg` prints dry-run output from `ClientContent`.
- `listAndRemove` lists and streams objects/versions into `Client.Remove`.
- `mainRm` parses flags, loops over CLI args, then optional stdin lines.

## Control flow
`checkRmSyntax` rejects `--version-id` with recursive/version/rewind, requires `--non-current` with both recursive and versions, restricts hidden `--purge`, requires target args or `--stdin`, requires `--force` for recursive/version/stdin modes, and requires both `--dangerous` and `--force` for namespace-wide removals.

`removeSingle` expands aliases, stats the object unless purge mode is active, tolerates specific HEAD errors that should not block deletion, applies age filters, prints dry-run if requested, constructs a single-content channel, calls `clnt.Remove`, and prints `rmMessage` results.

`listAndRemove` creates a list channel and a remove result channel. It lists objects according to recursive, incomplete, version, and rewind options. Normal mode filters prefix levels and age limits, then sends eligible contents to the remove channel while draining results. `--non-current` groups versions per object path, skips the latest live version, and removes only older/delete-marker versions matching age filters. It drains all results after closing the channel and emulates `rm -f` by not erroring when no object is found with `--force`.

`mainRm` builds `removeOpts` and applies the chosen helper for each positional target and each stdin line, preserving the first error.

## State and persistence
Mutates remote object storage state through `Client.Remove`. It may create delete markers in versioned buckets, delete specific versions, purge incomplete uploads, or bypass governance if authorized. No local persistence.

## Dependencies and integration points
Uses URL/stat helpers (`url2Stat`, `mustExpandAlias`, `newClientFromAlias`), client listing/removal APIs, `ListOptions`, age filters (`isOlder`, `isNewer`), MinIO S3 error mapping, `ClientContent`, global contexts, and global output/error helpers.

## Risks and edge cases
- Deletion is irreversible unless bucket versioning protects with delete markers, hence the extensive safety checks.
- The code tolerates some stat failures for delete markers and SSE-C but cannot apply age filters without mod time.
- Non-current version mode relies on listing order by object path and version order.
- WORM/object-lock errors are ignored in one recursive path when the message contains a specific string.
- Stdin mode shares global flags for every line and preserves the first error only.
- Hidden `--purge` bypasses normal stat/list behavior and is tightly constrained.

## Test signals
No direct tests in this subset. High-value tests would mock list/remove streaming, flag validation combinations, non-current grouping, dry-run output, age filter behavior, stdin iteration, and permission/WORM error handling.
