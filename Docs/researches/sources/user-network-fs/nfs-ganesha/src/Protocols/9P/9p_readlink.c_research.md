## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_readlink.c

Purpose: implements symlink target retrieval.

APIs and flow: `_9p_readlink` validates fid, initializes op context, calls `fsal_readlink`, encodes the returned UTF-8 string in `RREADLINK`, frees the FSAL-allocated string, and maps FSAL errors to errno.

State/dependencies: read-only over object state and depends on FSAL readlink allocation semantics.

Risks/tests: test invalid fid, non-symlink FSAL errors, long link targets vs msize, memory free on success, and no leak on error.
