# sources/user-network-fs/libsmb2/Makefile.am

Purpose: This is the root Automake file for libsmb2's autotools build. It wires subdirectories, pkg-config installation, distribution extras, and a convenience `test` target.

Important APIs and types: It uses Automake variables `SUBDIRS`, `ACLOCAL_AMFLAGS`, `pkgconfigdir`, `pkgconfig_DATA`, and `EXTRA_DIST`, plus the conditional `ENABLE_EXAMPLES`.

Control flow: When examples are enabled, `MAYBE_EXAMPLES` expands to `examples`. Automake builds `include`, `lib`, `utils`, the root directory, and optionally examples. The custom `test` target depends on subdirs and then runs `make test` under `tests`.

State and persistence behavior: Build outputs are autotools-generated Makefiles, libtool artifacts, installed pkg-config file `libsmb2.pc`, and any test outputs from the tests directory.

Dependencies and integration points: This file depends on conditionals and substitutions declared in `configure.ac`, and it delegates most real compilation to `include/Makefile.am`, `lib/Makefile.am`, `utils/Makefile.am`, `tests/Makefile.am`, and optionally `examples/Makefile.am`.

Risks: The root `test` target assumes the tests directory has been configured even though `tests` is not in `SUBDIRS`; it is only a direct `cd tests; make test` invocation. Changes to example conditionals or pkg-config generation need matching updates in `configure.ac`.

Test signals: `autoreconf && ./configure && make && make test` should create all Makefiles, build the library/utilities, install or stage `libsmb2.pc`, and run the delegated tests.
