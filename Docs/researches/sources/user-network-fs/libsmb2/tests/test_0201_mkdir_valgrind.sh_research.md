<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0201_mkdir_valgrind.sh -->
# sources/user-network-fs/libsmb2/tests/test_0201_mkdir_valgrind.sh

Purpose: Valgrind variant of mkdir/rmdir integration test.

Important APIs, types, and functions: Runs `prog_mkdir` and `prog_rmdir` under libtool/valgrind with leak checking and error exit code 1.

Control flow: Creates and removes `${TESTURL}/testdir`, treating valgrind findings as failures.

State and persistence behavior: Remote directory side effect is temporary.

Dependencies and integration points: Depends on valgrind/libtool, writable SMB share, and helper programs.

Risks: Valgrind can be slow and environment-sensitive. Fixed remote name can collide.

Test signals: Memory-safety signal for mkdir/rmdir sync paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0201_mkdir_valgrind.sh -->
