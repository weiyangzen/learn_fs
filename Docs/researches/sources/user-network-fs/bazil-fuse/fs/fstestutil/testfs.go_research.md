<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/testfs.go -->
# sources/user-network-fs/bazil-fuse/fs/fstestutil/testfs.go

Purpose: simple reusable filesystem node implementations for tests.

Important APIs, types, and functions: defines `SimpleFS`, embeddable `File`, embeddable `Dir`, and map-backed `ChildMap`.

Control flow: `SimpleFS.Root` returns its configured node. `File.Attr` sets a regular writable mode, `Dir.Attr` sets directory mode, and `ChildMap.Lookup` returns a child or ENOENT.

State and persistence behavior: `ChildMap` stores in-memory child nodes; no backing persistence.

Dependencies and integration points: implements bazil/fuse `fs.FS`, `fs.Node`, and `fs.NodeStringLookuper` interfaces for tests and benchmarks.

Risks and test signals: default permissive modes may not match specific permission tests; child nodes must be stable map-key-capable values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/testfs.go -->
