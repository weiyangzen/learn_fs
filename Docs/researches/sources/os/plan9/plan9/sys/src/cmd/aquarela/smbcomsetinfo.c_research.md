# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomsetinfo.c

Server handlers for legacy set-information commands.

Key functions:
- `smbcomsetinformation2` updates access/modify times on an open fid using DOS date/time fields and `dirfwstat`.
- `smbcomsetinformation` parses attributes, Unix-style SMB time, and path, then updates mtime via `dirwstat`.

Interactions:
- Uses time conversion helpers and Plan 9 `Dir` stat updates.

Notable details:
- `smbcomsetinformation2` appears to use fields from the new `Dir d` when filling missing old date/time parts, where it likely intended the old `Dir *od`.
- `smbcomsetinformation` calls `dirwstat(name, &d)` without prefixing the connected tree service path, unlike most path handlers.
