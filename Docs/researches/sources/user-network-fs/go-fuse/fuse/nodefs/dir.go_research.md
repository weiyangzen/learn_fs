## sources/user-network-fs/go-fuse/fuse/nodefs/dir.go

Purpose: directory response adapter for nodefs connector.

Important APIs/types/functions: `connectorDir` implements raw directory reads. `ReadDir` and `ReadDirPlus` pull directory entries from a node, add entries to `fuse.DirEntryList`, and include lookup entries for READDIRPLUS. `rawDir` captures directory-reading behavior.

Control flow: for each kernel directory read, the connector resolves the inode, obtains children or calls node `OpenDir`, serializes entries, and updates lookup counts for plus entries.

State and persistence: per-request state is the dir entry list; persistent state is inode children and lookup counts managed elsewhere.

Dependencies and integration: connects `nodefs.Inode` children with raw `fuse.DirEntryList`.

Risks and test signals: READDIRPLUS lookup accounting and directory offsets are tricky. Directory tests and handle count tests expose issues.
