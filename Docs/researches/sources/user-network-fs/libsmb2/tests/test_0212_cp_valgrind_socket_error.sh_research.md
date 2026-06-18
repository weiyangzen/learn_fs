<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0212_cp_valgrind_socket_error.sh -->
# sources/user-network-fs/libsmb2/tests/test_0212_cp_valgrind_socket_error.sh

Purpose: Socket-error fault-injection test for SMB copy upload and download paths.

Important APIs, types, and functions: Uses `LD_PRELOAD=./ld_sockerr.so`, `READV_CLOSE` loop, valgrind, and `../utils/smb2-cp`.

Control flow: Creates a local file, repeatedly copies to SMB with injected read failures, then repeatedly copies from SMB to local with injected failures.

State and persistence behavior: Local `testfile`/`testfile2` and remote `testfile` are touched. Injection state is per process environment.

Dependencies and integration points: Depends on ld_sockerr, valgrind/libtool, SMB server, and `NUM_CALLS` breadth.

Risks: The script does not verify every injected copy fails or succeeds in a specific way; it mainly catches crashes/leaks. Remote file must exist for download phase.

Test signals: Fault-tolerance signal for copy paths under socket failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0212_cp_valgrind_socket_error.sh -->
