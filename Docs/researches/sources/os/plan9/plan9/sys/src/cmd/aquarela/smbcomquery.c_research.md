# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomquery.c

Server handlers for legacy file information queries.

Key functions:
- `smbcomqueryinformation` stats a path under the tree and returns DOS attributes, mtime, size, and padding.
- `smbcomqueryinformation2` stats an open fid and returns date/time fields, size/allocation size, and attributes.

Interactions:
- Uses Plan 9 `dirstat`/`dirfstat`, time conversion helpers, and allocation rounding.

Notable details:
- Query-by-fid requires an open file descriptor; directory fids with `fd = -1` are not specially handled here.
