<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/buffer.go -->
# sources/user-network-fs/bazil-fuse/buffer.go

Purpose: internal byte buffer builder for low-level FUSE protocol messages.

Important APIs, types, and functions: defines `type buffer []byte`, `(*buffer).alloc`, `(*buffer).reset`, and `newBuffer`. `alloc` returns an `unsafe.Pointer` to newly extended storage, and `newBuffer` reserves space for `outHeader`.

Control flow: callers create a buffer with header capacity, append fixed-size segments through `alloc`, and reuse it with `reset`.

State and persistence behavior: state is only in-memory byte slices. `reset` zeroes the entire capacity before shortening to avoid stale protocol data reuse.

Dependencies and integration points: depends on `unsafe` and the package's FUSE wire header definitions.

Risks and test signals: pointer safety depends on callers not retaining pointers across reallocations. Tests should cover message encoding sizes and reuse zeroing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/buffer.go -->
