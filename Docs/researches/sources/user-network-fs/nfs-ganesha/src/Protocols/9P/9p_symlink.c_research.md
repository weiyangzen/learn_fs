## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_symlink.c

Purpose: implements symbolic link creation.

APIs and flow: `_9p_symlink` parses parent fid, name, link target, and gid, validates fid/write access/name, allocates a NUL-terminated target string, prepares mode 0777 attrs, calls `fsal_create(... SYMBOLIC_LINK ...)`, releases attrs and target buffer, drops the returned object ref, builds a symlink qid, and replies `RSYMLINK`.

State/dependencies: namespace mutation through FSAL; gid is parsed but not used. Depends on FSAL symlink create behavior and memory allocation helpers.

Risks/tests: test long names and link targets, read-only exports, ignored gid expectations, FSAL failure with non-null object, qid path correctness after put_ref, and target NUL termination.
