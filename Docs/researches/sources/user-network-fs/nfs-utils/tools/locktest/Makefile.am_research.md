# sources/user-network-fs/nfs-utils/tools/locktest/Makefile.am

Purpose: `tools/locktest/Makefile.am` builds the simple `testlk` lock exerciser.

Important build APIs and control flow: It declares `noinst_PROGRAMS = testlk`, builds it from `testlk.c`, and marks `Makefile.in` as maintainer-clean.

State, dependencies, and integration: The program is not installed; it is available in the build tree for manual or test use around advisory locking/NLM behavior.

Risks and test signals: Because it is `noinst`, downstream packages may not ship it. Tests should confirm it builds on platforms with POSIX `fcntl` locks and is available to any lock-related test harness expecting it.
