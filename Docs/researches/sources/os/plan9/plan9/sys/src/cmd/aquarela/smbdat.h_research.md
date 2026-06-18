# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbdat.h

Defines Aquarela SMB runtime data structures and dispatch table types.

Major contents:
- Forward declarations for session, tree, service, transaction, buffer, id-map, search, file, shared-file, CIFS session, and RAP structs.
- `SmbPeerInfo`, `SmbTransaction`, `SmbSession`, `SmbHeader`, and `SmbProcessResult`.
- `SmbOpTableEntry` and `SmbTrans2OpTableEntry` dispatch tables.
- `SmbGlobals` and logging flags.
- `SmbTree`, `SmbService`, `SmbSearch`, `SmbFile`, `SmbSharedFile`, `SmbLock`, `SmbCifsSession`, `SmbClient`, RAP and directory-info structs.
- String flag constants for SMB string parsing/formatting.

Interactions:
- Included by nearly all SMB implementation files through `headers.h`.

Notable details:
- Id-mapped object structs place `long id` first where `smbidmapadd/remove` expect to write/read ids through object pointers.
