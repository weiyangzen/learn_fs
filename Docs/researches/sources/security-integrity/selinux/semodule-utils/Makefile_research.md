# sources/security-integrity/selinux/semodule-utils/Makefile

Purpose: this top-level makefile coordinates the `semodule_package`, `semodule_link`, and `semodule_expand` utility subdirectories.

Important flow: `SUBDIRS` lists the utility directories. The `all`, `install`, `relabel`, and `clean` targets iterate over each subdir and invoke `$(MAKE) $@`, exiting on the first failure. The `test` target is empty.

State and persistence: this file does not build artifacts directly; all persistent outputs are delegated to subdirectory makefiles. Dependencies are a POSIX shell, `make`, and the subdirectory target contracts. Risks: the loop is serial, a missing subdirectory or unsupported target aborts the whole operation, and the empty `test` target can produce a false signal that tests exist or passed. Test signals are mostly build-system checks: `make all`, `make install DESTDIR=...`, `make clean`, and validating that each subdir installs the expected binaries and manpages.
