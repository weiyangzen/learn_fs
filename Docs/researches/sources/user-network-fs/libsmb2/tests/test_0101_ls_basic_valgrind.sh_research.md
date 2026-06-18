<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0101_ls_basic_valgrind.sh -->
# sources/user-network-fs/libsmb2/tests/test_0101_ls_basic_valgrind.sh

Purpose: Valgrind variant of the basic ls integration test.

Important APIs, types, and functions: Runs `prog_ls` under `libtool --mode=execute valgrind --leak-check=full --error-exitcode=77` for root, nonexistent, and existing directory cases.

Control flow: Same logical flow as the basic ls test, but wraps listing commands in valgrind and treats expected nonexistent-directory failure specially.

State and persistence behavior: Creates/removes remote `testdir`; valgrind output is redirected away except on selected paths.

Dependencies and integration points: Depends on valgrind, libtool wrapper, test helpers, and SMB server.

Risks: Valgrind availability and platform support affect test portability. Redirected logs can hide diagnostic detail on CI failure.

Test signals: Memory-leak/error signal through valgrind exit code 77.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0101_ls_basic_valgrind.sh -->
