<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0211_cp_valgrind.sh -->
# sources/user-network-fs/libsmb2/tests/test_0211_cp_valgrind.sh

Purpose: Valgrind version of the copy integration test.

Important APIs, types, and functions: Wraps `../utils/smb2-cp` with libtool/valgrind for upload, download, and nonexistent source checks.

Control flow: Same flow as basic copy, with leak/error detection and a final `cmp`.

State and persistence behavior: Creates local temporary files and a remote test file.

Dependencies and integration points: Depends on valgrind, libtool, `smb2-cp`, and SMB write permissions.

Risks: Valgrind output for the expected failure is redirected to `valgrind.out`; remote file cleanup is absent.

Test signals: Memory-safety and copy correctness signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0211_cp_valgrind.sh -->
