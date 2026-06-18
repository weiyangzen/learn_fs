# sources/test-tools/xfstests-bld/Makefile

Purpose: top-level makefile that materializes user-facing helper scripts from templates and installs them with bash completion links.

Important APIs and functions: variables `SCRIPTS`, `KBUILD_SCRIPTS`, `bindir`, and `completiondir`; targets `all`, `clean`, `install`, pattern rules for run-fstests and kernel-build templates.

Control flow: `all` builds wrapper scripts. Pattern rules substitute `@DIR@` with the current repository path and mark outputs executable. `install` copies scripts to `$(HOME)/bin` by default and creates completion symlinks.

State and persistence: creates generated executable scripts in the source tree and installs copies/symlinks under `DESTDIR` plus user-oriented directories.

Dependencies and integration: integrates with `run-fstests/*.sh.in`, `kernel-build/*.sh.in`, and bash-completion layout.

Risks: generated scripts bake in the current absolute path, so moving the repository requires regeneration. Default install paths target the invoking user's home.

Test signals: `make`, `make clean`, and `make install DESTDIR=...` should produce/remove/copy the expected wrapper scripts.
