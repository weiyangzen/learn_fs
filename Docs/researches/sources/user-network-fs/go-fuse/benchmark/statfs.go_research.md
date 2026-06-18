# sources/user-network-fs/go-fuse/benchmark/statfs.go

Purpose: builds a static in-memory file tree for stat/readdir benchmarks.

Important APIs/types: `StatFS` embeds `fs.Inode` and buffers `files map[string]fuse.Attr` before mount. `AddFile` records paths; `OnAdd` materializes all pending paths; `addFile` walks directory components, creates persistent directory inodes as needed, creates persistent `fs.MemRegularFile` leaves with requested attributes, and attaches children.

Control flow/state: before `OnAdd`, file metadata is stored in the map. After `OnAdd`, the source of truth is persistent inodes and `files` is set nil.

Dependencies/integration: used by `stat_test.go` and `example/statfs/main.go`. Risks include overwriting duplicate paths, default stable attrs for files, and memory use proportional to files plus content sizes. Tests validate hierarchy and benchmark stat/readdir.
