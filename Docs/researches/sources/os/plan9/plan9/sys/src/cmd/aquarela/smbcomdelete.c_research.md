# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomdelete.c

Server handler for wildcard file deletion.

Key functions:
- `smbremovefile` constructs a full path from service path, optional directory, and name, then calls `remove`.
- `smbcomdelete` parses search attributes and path pattern, splits directory/name, opens a directory cache, compiles SMB wildcard to regexp, removes matching files, and returns ack if at least one removal succeeds.

Interactions:
- Uses `smbpathsplit`, `smbmkdircache`, `smbmkrep`, `smbmatch`, and Plan 9 `remove`.

Notable details:
- Search attributes are logged but not used for filtering.
- Returns `ERRnoaccess` if no matched file was removed.
