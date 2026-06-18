## sources/user-network-fs/go-fuse/fuse/direntry.go

Purpose: encodes and decodes FUSE directory entry records for READDIR and READDIRPLUS responses.

Important APIs/types/functions: `DirEntry` holds name, inode, mode, and offset. `Parse` reads a kernel dirent buffer. `DirEntryList` owns output buffer state. `AddDirEntry`, `Add`, `AddDirLookupEntry`, `FixMode`, and `bytes` serialize entries and optional `EntryOut` prefixes. `modeToType` converts mode bits to dirent type.

Control flow: request handlers create a list with `NewDirEntryList`, append entries until the buffer is full, and then set `req.outPayload` to serialized bytes.

State and persistence: list state is per-request buffer plus current offset; no durable state.

Dependencies and integration: core to directory serving in raw `fuse`, `fs`, and `nodefs`.

Risks and test signals: alignment, offset, and type mistakes break `readdir`, `ls`, and READDIRPLUS. `randomtype_test.go`, `mem_test.go`, and directory stress tests exercise this code.
