## sources/user-network-fs/blobfuse2/component/libfuse/native_file_io.h

Purpose: Native C fast path for FUSE read/write/flush operations when a blobfuse handle exposes a Unix file descriptor. This avoids crossing into Go for cached/local file data.

Important APIs and flow: `file_handle_t` stores the Unix fd, the Go `handlemap.Handle` pointer encoded as an integer, operation count, and dirty flag. `allocate_native_file_object` allocates and zeroes this object for `fi->fh`; `release_native_file_object` frees it. `native_read_file` falls back to `libfuse_read` when fd is zero, otherwise calls `native_pread`. `native_write_file` similarly chooses `libfuse_write` or `native_pwrite`, marks dirty, increments a counter, and invokes `blobfuse_cache_update` every `CACHE_UPDATE_COUNTER` writes. `native_flush_file` calls Go `libfuse_flush` and clears dirty on success.

State and dependencies: The file owns malloc/free lifecycle for `fi->fh` and depends on `pread`, `pwrite`, `errno`, and Go-exported functions declared in `libfuse_defs.h`. Optional `ENABLE_READ_AHEAD` code defines a read-ahead handler but relies on fields not present in the visible `file_handle_t`.

Risks: No null check before dereferencing `fi` or `handle_obj` in native callbacks. Layout must match Go tests' unsafe casts. Dirty state is native-only and cache-update behavior is write-count based. Test coverage validates allocation/free and handler integration indirectly through libfuse tests.
