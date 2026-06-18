# sources/sync-backup/bup/dev/force-delete

## Purpose
Best-effort recursive deletion helper for stubborn test directories with restrictive permissions, ACLs, or Linux attributes.

## Important APIs, Types, and Functions
Runs `rm -rf`, optional `setfacl -Rb`, optional `chattr -R -aisu`, `chmod -R u+rwX`, `rm -r`, and diagnostics `find`, `lsattr`, `getfacl`.

## Control Flow
Attempts normal recursive delete first, then for remaining paths strips ACLs/attributes, fixes user permissions, retries removal, and records failure if the path remains.

## State and Persistence Behavior
Destructively removes requested paths and mutates metadata/permissions before deletion.

## Dependencies and Integration Points
Used by `make clean` for test tmp cleanup.

## Risks and Test Signals
Risks are destructive misuse on wrong paths and missing diagnostic tools. Signals are exit code 0 for full deletion, exit 1 with listings on failure.
