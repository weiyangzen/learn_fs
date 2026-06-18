# sources/security-integrity/selinux/Makefile

Purpose: top-level SELinux userspace build orchestrator.

Important variables/targets: defines `PREFIX`, optional subdirs, `SUBDIRS`, Python/Ruby wrapper subdirs, `CFLAGS`/`LDFLAGS`, `FTS_LDLIBS` detection, `DESTDIR` include/lib overrides, and aggregate targets `all`, `install`, `relabel`, `clean`, `test`, `install-pywrap`, `install-rubywrap`, `swigify`, `distclean`, `format`, and `check-format`.

Control flow: iterates subdirectories and invokes the same target; wrapper targets only visit Python-capable subdirs. Format targets find C/H files under subdirs and run clang-format.

State and dependencies: exports build flags and lib paths to submakes. Depends on compiler, `fts.h` probe, libsepol location, clang-format, and subdir Makefiles.

Risks and test signals: `-Werror` makes compiler drift visible. DESTDIR path propagation is heavily exercised by CI matrix build variants and clean checks.
