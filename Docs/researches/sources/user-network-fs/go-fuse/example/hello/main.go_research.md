# sources/user-network-fs/go-fuse/example/hello/main.go

Purpose: minimal go-fuse example analogous to libfuse `hello.c`, exposing one file at the mount root.

Important APIs/types: `HelloRoot` embeds `fs.Inode`, implements `NodeOnAdder` to create persistent `fs.MemRegularFile` child `file.txt`, and implements `NodeGetattrer` to set root permissions to `0755`. `main` parses `-debug`, mounts via `fs.Mount`, and waits.

Control flow/state: static in-memory tree populated at mount time. File content is the bytes `file.txt`; no backing persistence.

Dependencies/integration: demonstrates `fs.Options`, `fs.MemRegularFile`, `fuse.Attr`, and stable inode assignment. Risks are educational rather than production: fixed content and no cleanup beyond normal unmount. Test signal is successful mount and reading `/file.txt`.
