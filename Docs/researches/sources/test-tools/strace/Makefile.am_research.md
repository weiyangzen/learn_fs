<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/Makefile.am -->
# sources/test-tools/strace/Makefile.am

Purpose: top-level Automake input for strace, tying together subdirectories, distribution contents, coverage settings, release metadata, and maintainer-generated files.

Important declarations: `SUBDIRS = bundled src tests $(TESTS_M32) $(TESTS_MX32)` conditionally includes m32/mx32 test trees. `man_MANS`, `ACLOCAL_AMFLAGS`, coverage variables, and `EXTRA_DIST` define install/distribution behavior. Targets include `srpm`, `.version`, `dist-hook`, `news-check`, `clean-local`, `ChangeLog`, and `CREDITS`.

Control flow: Automake conditionals enable compat test dirs based on configure results. `dist-hook` writes tarball version/year/manpage date files. Maintainer-mode targets regenerate `ChangeLog` from Git and `CREDITS` from `CREDITS.in`.

State and persistence: writes `.version`, `.tarball-version`, `.year`, doc date files, generated `ChangeLog`, generated `CREDITS`, and removes mpers build dirs in `clean-local`.

Dependencies and integration: integrates Autoconf variables, build-aux scripts, coverage macros, Debian/RPM packaging files, docs, and bundled headers.

Risks: release checks depend on UTC date and exact NEWS headline format. Maintainer targets depend on Git and helper scripts. Distribution completeness depends on `EXTRA_DIST` staying current. Test signals: `autoreconf && ./configure && make distcheck`, `make news-check`, and `make srpm` are the strongest validation points.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/Makefile.am -->
