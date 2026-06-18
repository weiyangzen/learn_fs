## sources/security-integrity/ecryptfs-utils/tests/kernel/read-dir/test.c

Purpose: C negative test for `read()` on an eCryptfs directory. It verifies the regression fix for LP 719691: reading a directory should fail and set `errno` to `EISDIR`, not `EINVAL`.

Important APIs and functions: `main`, `open(argv[1]/.)`, `read`, `close`, `errno` validation. Control flow opens the directory read-only, reads into a 4096-byte buffer, fails if read succeeds, checks `errno == EISDIR`, then exits pass.

State and persistence: No writes or persistent state. Dependencies are VFS/eCryptfs directory read behavior. Integration is through `read-dir.sh`. Risks include strict errno expectations across kernels; a different failure mode still indicates compatibility risk for applications relying on standard directory semantics. Test signals are `0` pass, `1` semantic failure, `2` usage/setup error.
