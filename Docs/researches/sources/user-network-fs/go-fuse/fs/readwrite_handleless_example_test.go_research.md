## sources/user-network-fs/go-fuse/fs/readwrite_handleless_example_test.go

Purpose: runnable example of a writable file implemented directly on a node without a separate file handle.

Important APIs/types/functions: `bytesNode` stores bytes and a mutex. It implements `NodeGetattrer`, `NodeSetattrer`, `NodeReader`, `NodeWriter`, and `NodeOpener`. Helpers `getattr` and `resize` maintain `fuse.Attr` fields. `Example_handleLess` mounts the node using `fs.Mount`.

Control flow: `Open` returns nil handle with cache flags. `Read` copies from the node byte slice by offset. `Write` resizes and copies into the slice. `Setattr` handles truncation through `GetSize`. `Getattr` reports size/mode under lock.

State and persistence: file content exists only in `bytesNode.data`; mutex protects concurrent kernel calls. No durable storage.

Dependencies and integration: demonstrates handleless high-level file APIs, `fuse.ReadResultData`, `FOPEN_KEEP_CACHE`, and set-attribute resize semantics.

Risks and test signals: example code is compiled and can be run as documentation. The main risk is concurrent access; the mutex is the intended pattern for node-backed mutable state.
