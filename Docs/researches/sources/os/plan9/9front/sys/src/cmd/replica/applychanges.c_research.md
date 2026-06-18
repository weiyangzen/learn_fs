# File Research: sources/os/plan9/9front/sys/src/cmd/replica/applychanges.c

Pushes local/client changes to a server tree using a replica client database and proto traversal.

For each proto file, compares client metadata, server metadata, and database metadata to detect create/create, update/remove, update/update, metadata, and removal conflicts. Applies adds, content changes, metadata changes, and deletes when safe.

Supports dry-run/verbose, uid syncing, proto selection, exclusion paths, and path filters. File copy preserves mode, gid, optional uid, and mtime.
