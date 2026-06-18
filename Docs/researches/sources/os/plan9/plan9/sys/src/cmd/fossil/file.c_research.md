# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/file.c

High-level fossil file and directory object layer built over `Source` streams.

Each `File` has file metadata (`DirEntry`), a data `Source`, and, for directories, a metadata `Source` containing packed directory entries. Walking opens children from metadata blocks and caches live child `File` objects under their parent. File operations implement create, read, write, append, truncate, stat/wstat, remove, clri, refcounting, directory enumeration, metadata flushing, and temporary/no-archive flag propagation.

The file enforces root immutability, read-only modes, directory vs file checks, empty-directory removal, and lock ordering. Snapshot support is integrated through `fileSnapshot`, which copies source entries into snapshot directories, and `fileWalkSources`, which forces copy-on-write down to the source-entry blocks before snapshot linking.
