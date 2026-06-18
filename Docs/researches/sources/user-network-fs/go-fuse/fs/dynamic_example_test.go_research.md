# sources/user-network-fs/go-fuse/fs/dynamic_example_test.go

Purpose: example of a dynamically discovered filesystem where numbers are files or directories and stable inode numbers deduplicate repeated nodes.

Important types/functions: `numberNode` embeds `fs.Inode` and stores `num`; `isPrime` and `numberToMode` choose file vs directory; `Readdir` lists smaller numbers; `Lookup` parses a child name, validates bounds, sets `StableAttr{Mode, Ino:uint64(i)}`, creates a new inode, and returns it; `Example_dynamic` mounts root `10`.

State/dependencies: no persistent backing store; stable inode numbers deduplicate repeated lookups across paths.

Integration/risks: demonstrates `NodeLookuper`, `NodeReaddirer`, and dynamic hard-link-like identity. Risks are pedagogical: generated filesystem is synthetic and prime function treats edge values simply. Build/example coverage is primary signal.
