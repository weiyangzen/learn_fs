# sources/test-tools/xfstests-bld/fstests-bld/Makefile

Purpose: makefile for fetching, building, cleaning, and packaging the component repositories used in an xfstests appliance.

Important APIs and functions: variables `REPOS`, `SUBDIRS`, `SCRIPTS`; targets `all`, `all-clean-first`, `clean`, `realclean`, `tarball`, and `run-fstests/util/zerofree`.

Control flow: `all` runs `./get-all` then `./build-all`. `all-clean-first` removes build products and invokes `build-all --clean-first`. `clean` delegates clean to subdirectories, handles xfsprogs realclean, and removes generated build output. `realclean` additionally removes fetched repositories.

State and persistence: creates fetched repository directories, `bld`, generated scripts, version files, `xfstests`, and optional static `zerofree`.

Dependencies and integration: integrates with `get-all`, `build-all`, `gen-tarball`, component subprojects, and system `cc`.

Risks: `realclean` is destructive to fetched repos. The clean loop ignores subdirectories without Makefiles, which is useful but can leave non-Makefile build products.

Test signals: `make all`, `make all-clean-first`, and `make tarball` are the primary build validation paths.
