# File Research: sources/os/plan9/plan9/sys/src/cmd/dossrv/dat.h

Central data-definition header for `dossrv`.

Key contents:
- FAT partition type constants for FAT12, FAT16, FAT32, extended FAT variants, and DMDDO.
- On-disk structures: `Dospart`, `Dosboot`, `Dosboot32`, `Fatinfo`, and `Dosdir`.
- In-memory filesystem state: `Dosbpb` for parsed BPB/FAT geometry and allocation state.
- Directory traversal state: `Dosptr`, including current directory-entry address/offset, parent address/offset, cached sector, and cluster cursor.
- Served filesystem state: `Xfs`, with backing device name/qid/fd, root qid, FAT32 flag, offset, refcount, and parsed private state.
- Per-fid state: `Xfile`, with fid, open flags, qid, attached `Xfs`, and `Dosptr`.
- Little-endian helpers `GSHORT`, `GLONG`, `PSHORT`, and `PLONG`.
- Request/reply buffer globals and maximum 9P data size.

Filesystem relevance:
- Defines the server’s FAT disk layout, 9P fid state, qid mapping, and cached traversal model.
