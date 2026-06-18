<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0301_cat_valgrind.sh -->
# sources/user-network-fs/libsmb2/tests/test_0301_cat_valgrind.sh

Purpose: Valgrind variant of the cat integration test.

Important APIs, types, and functions: Runs `prog_cat` under libtool/valgrind with leak checking and error exit code 1.

Control flow: Reads `${TESTURL}/CAT` and discards output.

State and persistence behavior: No persistent state.

Dependencies and integration points: Depends on valgrind/libtool and remote `CAT` fixture.

Risks: No content assertion; only success and memory-safety are checked.

Test signals: Memory-safety signal for async open/read/close/disconnect path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0301_cat_valgrind.sh -->
