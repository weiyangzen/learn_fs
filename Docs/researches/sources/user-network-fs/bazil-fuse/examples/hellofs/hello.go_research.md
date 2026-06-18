<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/examples/hellofs/hello.go -->
# sources/user-network-fs/bazil-fuse/examples/hellofs/hello.go

Purpose: minimal hello-world FUSE filesystem exposing a single read-only `hello` file.

Important APIs, types, and functions: implements `FS.Root`, `Dir.Attr`, `Dir.Lookup`, `Dir.ReadDirAll`, `File.Attr`, and `File.ReadAll`; uses `fuse.Mount` and `fs.Serve`.

Control flow: `main` parses one mountpoint, mounts with FS name/subtype, serves `FS{}`, and defers connection close. The root directory returns the fixed file for name `hello` and ENOENT otherwise.

State and persistence behavior: no mutable or persistent state; `greeting` is a constant.

Dependencies and integration points: demonstrates the core `fs.Node`, lookup, directory listing, and read-all interfaces.

Risks and test signals: read-only behavior depends on mode bits and lack of write handlers. Signal is successful mount and `cat hello` returning `hello, world`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/examples/hellofs/hello.go -->
