## sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_commit.c

Purpose: implements NFSv3 `COMMIT`.

APIs and flow: `nfs3_commit` converts the file handle, calls `fsal_commit` with offset/count, drops retryable errors, maps nonretryable errors with weak cache consistency data, and on success returns WCC data plus `NFS3_write_verifier`. Free function is a no-op.

State/dependencies: flushes persistent storage through FSAL and reports verifier state. Depends on dispatcher write permissions, FSAL commit, WCC helpers, and global write verifier.

Risks/tests: test whole/partial commit ranges, FSAL retryable failures, verifier stability across server restart rules, WCC before/after data, and stale handle behavior.
