# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbfile.c

SmbFile close/free helper.

Key functions:
- `smbfilefree` releases shared-file state, closes fd, frees file name and object.
- `smbfileclose` logs close, removes the fid id-map entry, and frees the file.

Interactions:
- Used by close handlers and failure cleanup in open handlers.
- Calls `smbsharedfileput` to update share-deny and delete-on-close state.

Notable details:
- `smbidmapremove` relies on `SmbFile.id` being the first field written by the id map.
