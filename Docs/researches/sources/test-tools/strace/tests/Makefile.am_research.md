<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/Makefile.am -->
## sources/test-tools/strace/tests/Makefile.am

Purpose: Automake input that defines the strace test harness, helper library, generated decoder tests, standalone test binaries, scripts, data files, installable test payloads, and cleanup/prerequisite rules.

Important APIs/types/functions: Defines `AM_CPPFLAGS`, `AM_CFLAGS`, `AM_LDFLAGS`, `libtests_a_SOURCES`, `check_PROGRAMS`, `DECODER_TESTS`, `MISC_TESTS`, `STACKTRACE_TESTS`, `TESTS`, `check_SCRIPTS`, `check_DATA`, `EXTRA_DIST`, `TEST_LOG_COMPILER`, and `AM_TEST_LOG_FLAGS`. Includes `pure_executables.am`, `secontext.am`, `gen_tests.am`, and `../src/scno.am`.

Control flow: Configure-time substitutions set architecture, kernel long size, native architecture, bundled header include paths, and optional SELinux/stacktrace settings. Automake builds `libtests.a`, compiles hundreds of check programs including the files in this group, expands generated tests, runs each `.test` through `run.sh` with architecture environment, and optionally installs tests under `$(libexecdir)/strace/tests$(MPERS_NAME)`.

State and persistence: Build artifacts include `libtests.a`, many test executables, generated `ksysent.h`, per-test `.dir` directories, logs, and optional installed test assets. Cleanup removes generated directories and `ksysent.h`.

Dependencies and integration: Connects test C files to helper sources (`tests.h`, socket, print, pid namespace, secontext, xlat utilities), optional `clock_LIBS`, `mq_LIBS`, `dl_LIBS`, `m_LIBS`, pthread, valgrind rules, bundled Linux UAPI headers, and stacktrace libraries.

Risks: The file is a central registry; missing a wrapper executable or `.test` entry silently reduces coverage. Per-target flags and link libraries must track source requirements, especially BPF clock helpers, pthread attach/thread tests, large-file `_FILE_OFFSET_BITS=64`, and optional stacktrace XFAIL behavior.

Test signals: `make check`, `make check-prerequisites-local`, generated `ksysent.h` correctness, installed-test layout under `ENABLE_INSTALL_TESTS`, and absence of stale test directories after `clean-local-check`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/Makefile.am -->
