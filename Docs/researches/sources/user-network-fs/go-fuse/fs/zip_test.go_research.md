## sources/user-network-fs/go-fuse/fs/zip_test.go

Purpose: tests ZIP-backed read-only filesystem construction and on-add tree population.

Important APIs/types/functions: `testData` defines archive contents. `createZip` writes deterministic zip entries. `byteReaderAt` adapts a byte slice for `zip.NewReader`. `TestZipFS` and `TestZipFSOnAdd` mount zip contents and verify file reads and directory layout.

Control flow: create in-memory zip data, build a zip reader, construct the zip FS, mount it, and read paths through the kernel. The on-add variant verifies child population at mount time.

State and persistence: archive bytes are in memory; mounted files are read-only views over zip entry data. No writes persist back into the archive.

Dependencies and integration: uses Go `archive/zip`, the `fs` zip example implementation, and normal FUSE read/stat paths.

Risks and test signals: catches tree-building mistakes, path normalization issues, and reader-at offset bugs in compressed file serving.
