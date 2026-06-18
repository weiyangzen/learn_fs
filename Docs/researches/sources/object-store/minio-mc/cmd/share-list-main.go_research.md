# sources/object-store/minio-mc/cmd/share-list-main.go

## Purpose
Implements `mc share list`/`ls`, listing locally persisted, unexpired upload or download share entries.

## Important APIs, types, and functions
- `shareList` registers the command and `ls` short name.
- `checkShareListSyntax` requires one argument: `upload` or `download`.
- `doShareList` loads the selected share DB and prints each entry as `shareMessage`.
- `mainShareList` validates args, sets colors, initializes share config, and executes listing.

## Control flow
`mainShareList` initializes the share directory and DB files if missing, then calls `doShareList`. The DB `Load` operation prunes expired entries before printing. Each remaining map entry is printed with its object URL, share URL, time left, and optional content type.

## State and persistence
Read-mostly local state. It can update the selected JSON DB indirectly because `Load` deletes expired shares and saves the pruned result.

## Dependencies and integration points
Uses share DB/config helpers, `shareMessage`, MinIO CLI/global output, and `probe.Error`.

## Risks and edge cases
- Map iteration order is nondeterministic, so output ordering can vary.
- Expired entry pruning means a list operation mutates local config files.
- There is no filtering by target, age, or content type.

## Test signals
No direct tests. Useful tests would cover syntax validation, upload vs download DB selection, expired pruning side effect, and message fields.
