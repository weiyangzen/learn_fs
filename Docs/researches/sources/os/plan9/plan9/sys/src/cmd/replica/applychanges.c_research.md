# File Research: sources/os/plan9/plan9/sys/src/cmd/replica/applychanges.c

Read status: complete, 332 lines.

`replica/applychanges` pushes changes from a client tree/database to a server tree. It enumerates a proto-described client tree, compares it with the local replica database and server filesystem, detects conflicts, and copies, removes, or updates metadata.

`walk` is the main decision function. It skips excluded paths, marks database entries, detects create/create, update/remove, update/update, metaupdate/remove, and metaupdate/metaupdate conflicts, and applies additions, content changes, and metadata changes when not in dry-run mode.

After enumeration, `main` walks unmarked database entries to detect removals and remove server-side files if safe. Helpers `copyfile`, `copy1`, and `metafile` copy contents and update mode/gid/uid/mtime.

Options include dry-run/verbose behavior, uid preservation, proto selection, and exclusions.

Filesystem relevance: high. It is a two-tree synchronizer with explicit file metadata conflict checks.
