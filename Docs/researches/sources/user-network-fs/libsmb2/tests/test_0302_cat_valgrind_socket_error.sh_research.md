<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0302_cat_valgrind_socket_error.sh -->
# sources/user-network-fs/libsmb2/tests/test_0302_cat_valgrind_socket_error.sh

Purpose: Socket-error fault-injection test for async cat.

Important APIs, types, and functions: Loops `READV_CLOSE` values under `LD_PRELOAD=./ld_sockerr.so` and valgrind while running `prog_cat`.

Control flow: Each iteration injects a readv failure at a different call index during read of `${TESTURL}/CAT`.

State and persistence behavior: No persistent state beyond per-process injection variables.

Dependencies and integration points: Depends on ld_sockerr, valgrind/libtool, and remote `CAT` fixture.

Risks: May miss paths if `NUM_CALLS` is too low/high. It checks tolerance to failures more than semantic error codes.

Test signals: Crash/leak resilience signal for async read under socket failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0302_cat_valgrind_socket_error.sh -->
