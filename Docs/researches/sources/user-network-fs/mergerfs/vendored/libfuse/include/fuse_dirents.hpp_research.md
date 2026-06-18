<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_dirents.hpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_dirents.hpp

Purpose: `fuse_dirents_t` aggregates directory entries before replying to FUSE readdir/readdirplus requests. It stores raw data bytes and an offset index using `kvec_t`.

Important APIs: `fuse_dirents_init`, `fuse_dirents_free`, and `fuse_dirents_reset` manage the vectors. `fuse_dirents_add` has overloads for POSIX `dirent` and vendored `fs::dirent64`, each taking an explicit name length.

Control flow and state: entries are appended to `data`, and per-entry offsets are appended to `offs`. The state is in heap buffers owned by `kvec`; reset preserves allocations while clearing logical contents, and free releases them.

Risks and test signals: `kvec` allocation failures are not type-safe unless implementations check `realloc`. Offset accounting and record alignment are critical for kernel parsing. Tests should add entries of varied name lengths, reset/reuse the container, and verify byte offsets and final reply size.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_dirents.hpp -->
