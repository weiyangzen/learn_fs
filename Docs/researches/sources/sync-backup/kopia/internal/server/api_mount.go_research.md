# sources/sync-backup/kopia/internal/server/api_mount.go

Purpose: implements HTTP APIs for creating, listing, querying, and deleting mounted snapshot/object roots.

Important APIs/types/functions: `handleMountCreate`, `handleMountGet`, `handleMountDelete`, and `handleMountList`.

Control flow: create decodes mount request, resolves the requested root object into a filesystem directory, calls server mount-controller lookup/creation, and returns mount metadata. Get returns an existing controller for an object ID, delete removes and unmounts it, and list serializes all current mounts.

State and persistence behavior: mutates the server's in-memory `mounts` map and creates OS mount/WebDAV/FUSE state through `mount.Controller`.

Dependencies and integration points: connects server API, repository object IDs, restore filesystem view, and `internal/mount`.

Risks and test signals: object IDs must be validated, unmount failures need surfacing, and controller lifecycle must avoid leaked mounts. Integration tests should cover create/get/list/delete and duplicate create behavior.
