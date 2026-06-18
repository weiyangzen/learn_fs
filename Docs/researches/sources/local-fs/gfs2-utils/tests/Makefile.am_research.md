# File Research: sources/local-fs/gfs2-utils/tests/Makefile.am

Automake test harness for gfs2-utils.

Defines:
- Test scripts: `fsck.gfs2-tester.sh`, `rgrifieldscheck.sh`, `rgskipcheck.sh`
- Distributed files: autotest inputs, package template, `atlocal.in`
- Generated/cleaned files: `atlocal`, `atconfig`, `testvol`, `gfs2-utils.spec`
- `noinst_PROGRAMS = nukerg`

Builds `nukerg` from `nukerg.c` and links it against `libgfs2` and UUID libs.

Autotest integration:
- `TESTSUITE_AT` includes `testsuite.at`, `mkfs.at`, `fsck.at`, `edit.at`, `tune.at`.
- `check-local` and `installcheck-local` run the generated `testsuite`.
- `package.m4` is generated from package metadata.
- `AUTOM4TE`/`AUTOTEST` create the `testsuite`.

Research notes:
- `AUTOTEST_PATH` for installcheck includes installed sbin, `gfs2/libgfs2`, and tests.
