<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0102_ls_basic_socket_error.sh -->
# sources/user-network-fs/libsmb2/tests/test_0102_ls_basic_socket_error.sh

Purpose: Fault-injection ls test that closes the SMB socket at successive `readv` calls.

Important APIs, types, and functions: Uses `ld_sockerr.so` through `LD_PRELOAD` and loops `READV_CLOSE` from 1 to `NUM_CALLS` while running `prog_ls` under valgrind.

Control flow: For each injected failure point, the helper interposes `readv`; the script accepts process completion without invoking `failure`, aiming to expose crashes/leaks under broken sessions.

State and persistence behavior: No persistent local state. Remote state is only listing operations.

Dependencies and integration points: Depends on `ld_sockerr.so`, valgrind, ltrace-derived `NUM_CALLS`, and SMB server behavior.

Risks: If `NUM_CALLS` is inaccurate, parts of the read path are not exercised. The script may not assert that failures occurred, only that the program tolerated them.

Test signals: Socket-error resilience signal across multiple read points.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0102_ls_basic_socket_error.sh -->
