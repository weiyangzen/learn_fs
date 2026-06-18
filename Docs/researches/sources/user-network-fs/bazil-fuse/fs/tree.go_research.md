# sources/user-network-fs/bazil-fuse/fs/tree.go

Purpose: `tree.go` provides a small read-only directory tree implementation for users who want to expose a static path hierarchy through `fs.Serve`. The tree directories are read-only, but the leaf `Node` values inserted into the tree may implement writable behavior themselves.

Important APIs, types, and functions: `Tree` embeds the internal `tree` and implements `Root() (Node, error)`. `(*Tree).Add(path string, node Node)` installs nodes by slash-separated path. Internal `treeDir` stores a basename and child node, while `tree` stores an ordered slice of entries and implements `Attr`, `Lookup`, and `ReadDirAll`.

Control flow: `Add` cleans the path by prefixing `/`, using `path.Clean`, stripping the leading slash, and splitting on `/`. It walks existing `tree` nodes, creating intermediate `tree` directories as needed. If an existing path conflicts with the new path, or a prefix is already a non-tree node, it panics. Lookup performs a linear scan. `ReadDirAll` emits `fuse.Dirent` values in insertion order.

State and persistence behavior: All state is in memory in `tree.dir`. There is no synchronization; the comment explicitly says `Add` is only safe before serving requests. Runtime request handling is read-only with no persistence beyond process memory.

Dependencies and integration points: The file integrates with the `fs` package's `Node` interfaces and the low-level `fuse.Attr` and `fuse.Dirent` types. It uses `context`, `os.FileMode`, `path`, `strings`, and `syscall.ENOENT`.

Risks: Panics are part of the configuration-time contract, so callers must avoid duplicate or overlapping paths. Directory lookup is O(n) per directory. No directory entry type or inode is set in `ReadDirAll`, so clients may need follow-up getattr calls. Concurrent mutation after serving begins is unsafe.

Test signals: This file has no direct tests in this subset, but `serve_test.go` exercises directory lookup and `ReadDirAll` behavior through similar test nodes.
