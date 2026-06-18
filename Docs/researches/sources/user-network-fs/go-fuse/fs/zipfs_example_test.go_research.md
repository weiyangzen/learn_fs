## sources/user-network-fs/go-fuse/fs/zipfs_example_test.go

Purpose: example implementation of a read-only filesystem backed by a zip archive.

Important APIs/types/functions: `zipFile` stores a `zip.File`, implements `NodeGetattrer`, `NodeOpener`, and `NodeReader`; it reports mode/size, opens zip entry readers, and reads by offset. `zipRoot.OnAdd` walks archive entries and creates persistent child inodes. `Example_zipFS` demonstrates mount setup.

Control flow: on mount, the root iterates zip entries, creates directories/files as inodes, and links them into the tree. File reads open an archive entry reader, seek/copy as needed, and return `ReadResultData`.

State and persistence: archive metadata and bytes are immutable backing state. Inode tree is materialized in memory at mount time.

Dependencies and integration: integrates Go `archive/zip` with `fs.Inode`, `StableAttr`, and FUSE stat/open/read callbacks.

Risks and test signals: example must handle nested directories, file modes, and repeated reads without leaking readers. It is covered by example compilation and related zip tests.
