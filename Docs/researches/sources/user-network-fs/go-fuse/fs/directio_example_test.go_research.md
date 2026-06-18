# sources/user-network-fs/go-fuse/fs/directio_example_test.go

Purpose: documentation example showing direct I/O for per-open dynamic file content.

Important types/functions: `bytesFileHandle` implements `FileReader` over per-handle bytes; `timeFile.Open` rejects write flags, captures current time into a new handle, and returns `FOPEN_DIRECT_IO`; `Example_directIO` mounts a root and adds a persistent `clock` file in `OnAdd`.

Control flow/state: each open gets independent content. Direct I/O prevents kernel page cache from hiding changes between opens.

Dependencies/integration: demonstrates `fs.Mount`, `FileReader`, `NodeOpener`, persistent inodes, and `fuse.ReadResultData`. Risk: the write-flag check uses `fuseFlags` instead of `openFlags`, so the example as written does not actually reject writes based on caller flags. Example is manual and not assertion-based.
