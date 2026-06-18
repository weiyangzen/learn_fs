# sources/test-tools/ior/testing/libnfs/src/aiori-LIBNFS-test.c

Purpose: CMocka integration tests for the LIBNFS AIORI backend, using a real NFS URL mapped to a local folder so backend operations can be verified via local filesystem checks.

Important APIs and functions: `main()` validates arguments, checks NFS availability, builds CMocka tests, and runs them. Helpers include `check_server_state()`, `clear_folder()`, `create_local_file()`, `read_local_file()`, `verify_local_file()`, and `local_directory_exists()`. Test setup/teardown call `libnfs_aiori.initialize()`/`finalize()` and clear the local folder. Test cases cover create, write, read at offsets, read/write combination, append, truncate, remove, mkdir/rmdir, and file size.

Control flow: the test binary expects two arguments: local folder path and NFS URL. It clears the folder, retries server availability up to five times, waiting through NFS grace mode, then runs each test with the shared `test_infrastructure_data` as prestate. Each test invokes the backend and asserts local side effects.

State and persistence: each test mutates the local folder and the NFS export. Setup and teardown clear the folder using `rm -rf folder/*`. Backend options store the NFS URL. No persistent state should remain after teardown if cleanup succeeds.

Dependencies and integration: depends on CMocka, libnfs (`nfsc/libnfs.h`), the LIBNFS AIORI backend, local POSIX file/stat helpers, and an external NFS server configuration matching the local folder.

Risks: `clear_folder()` builds a shell command from an argument without quoting, which is unsafe for spaces or metacharacters. `check_server_state()` does not check URL parse failure before using fields. Some helper path length checks omit separator/NUL details. Tests assume local folder view is coherent with NFS server writes immediately. The retry loop can run longer than expected in repeated grace mode. Duplicate `stdio.h` include is harmless.

Test signals: this file itself is an integration test. Passing signals include all CMocka cases succeeding against a live NFS server. Failure modes identify backend semantics for flags, offset handling, append/truncate behavior, directory operations, and stat size.
