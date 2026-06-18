<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/Makefile.am -->
# sources/user-network-fs/libsmb2/tests/Makefile.am

Purpose: Defines the libsmb2 test programs, test scripts, helper preload library, and check-time wiring for Automake.

Important APIs, types, and functions: Sets include paths and warning flags, lists `check_PROGRAMS`, `TESTS`, `EXTRA_PROGRAMS = ld_sockerr`, source assignments, `ld_sockerr.so` build command, and script installation through `bin_SCRIPTS`.

Control flow: Automake builds helper binaries, creates an LD_PRELOAD shared object from `ld_sockerr.c`, and runs the shell tests as the check suite.

State and persistence behavior: No runtime persistence except generated binaries and `ld_sockerr.so` in the build tree.

Dependencies and integration points: Integrates tests with libsmb2 library, libtool, shell scripts, and the utils directory. It is the hub for the test files in this subset.

Risks: Manual `gcc -shared` command may bypass normal Automake portability flags. Test scripts require `TESTURL` and a live SMB server, so default `make check` is environment-dependent.

Test signals: The listed `TESTS` provide the suite's direct execution signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/Makefile.am -->
