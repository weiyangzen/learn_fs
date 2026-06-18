# sources/user-network-fs/go-fuse/fs/mem.go

Purpose: simple in-memory file and symlink node implementations for examples/tests/static filesystems.

Important types/functions: `MemRegularFile` embeds `Inode`, owns `Data []byte` and `fuse.Attr` under mutex, and implements open/read/write/getattr/setattr/flush/allocate. `Open` returns `FOPEN_KEEP_CACHE`; `Write` grows data and copies bytes; `Setattr` resizes on size changes; `Allocate` grows capacity/data and respects platform `keepSizeMode`. `MemSymlink` stores attrs and symlink target bytes, implementing `Readlink` and `Getattr`.

State/persistence: all content is process memory; data is lost on unmount/process exit.

Risks/test signals: `Setattr` slicing to larger size without ensuring capacity can panic if asked to grow; `Read` assumes non-negative offset. Used heavily by examples and benchmarks, with indirect tests through in-memory filesystems.
