# sources/security-integrity/selinux/libsepol/include/Makefile

Purpose: Installs libsepol public headers into a destination include tree.

Important APIs and targets: The `install` target creates `$(INCDIR)`, `$(INCDIR)/policydb`, and `$(INCDIR)/cil`, then installs `sepol/*.h`, `sepol/policydb/*.h`, and CIL public headers from `$(CILDIR)/include/cil/*.h`.

Control flow: `all` is empty; `install` performs directory checks and `install -m 644` copies. Variables include `PREFIX`, `INCDIR`, and `CILDIR`.

State and persistence: The makefile writes only installation artifacts under `$(DESTDIR)$(PREFIX)/include/sepol`.

Dependencies and integration points: Used by distro/package builds and top-level libsepol install flows. It bridges libsepol and CIL public header installation.

Risks: `wildcard` expansion can silently omit headers if paths are wrong. Install mode and destination layout are ABI/API visible to downstream builds.

Test signals: `make install DESTDIR=...` followed by compile tests using installed headers validates the contract.
