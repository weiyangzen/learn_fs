# sources/sync-backup/kopia/internal/fusemount/fusefs.go

Purpose: implements go-fuse node adapters that expose a Kopia `fs.Directory` tree as a read-only FUSE filesystem on supported Unix platforms.

Important APIs/types/functions: `fuseNode`, `fuseFileNode`, `fuseFileHandle`, `fuseDirectoryNode`, `fuseSymlinkNode`, `goModeToUnixMode`, `populateAttributes`, `Getattr`, `Open`, `Read`, `Release`, `Lookup`, `Readdir`, `Readlink`, `entryToFuseMode`, `newFuseNode`, and `NewDirectoryNode`. Compile-time assertions ensure go-fuse interfaces are implemented.

Control flow: directory lookup asks the underlying `fs.Directory` for a child, maps missing entries to `ENOENT`, creates the appropriate node, and populates attributes. Readdir iterates all children into `fuse.DirEntry` values. File open obtains an `fs.Reader`; reads seek to the requested offset, read into FUSE's buffer, and return `fuse.ReadResultData`. Symlink reads delegate to `fs.Symlink.Readlink`.

State/persistence behavior: node state wraps immutable snapshot entries plus open file handles. File handle state is protected by a mutex because FUSE may issue concurrent reads on the same handle. No writes, creates, deletes, or persistence mutations are implemented.

Dependencies/integration: depends on `github.com/hanwen/go-fuse/v2`, Kopia `fs` interfaces, and repository logging. Build tags exclude Windows, OpenBSD, and FreeBSD.

Risks/test signals: unsupported entry types return `EIO` through lookup creation. Attributes use a fake block size and set uid/gid from entry owner metadata. There are no tests in this subset, so integration coverage likely comes from mount-level tests.
