# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbdircache.c

Directory cache helper for SMB directory/pattern operations.

Key functions:
- `smbmkdircache` builds a full path from tree service root and requested path, opens it, reads all directory entries with `dirreadall`, and stores them in `SmbDirCache`.
- `smbdircachefree` frees entry buffer and cache object.

Interactions:
- Used by delete and likely transaction2 find handlers outside this group.

Notable details:
- Cache stores current index `i`, though this file only initializes it.
