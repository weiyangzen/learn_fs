<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/test/Makemodule.am -->
# sources/security-integrity/acl/test/Makemodule.am

Purpose: Automake test module wiring ACL functional tests, fixture files, and the deterministic passwd/group preload library into `make check`. The file is 38 lines.

Important APIs and targets: Important declarations or variables include `XFAIL_TESTS`, `TESTS`, `EXTRA_DIST`, `check_LTLIBRARIES`, `libtestlookup_la_SOURCES`, `libtestlookup_la_CFLAGS`, `libtestlookup_la_LDFLAGS`, `AM_TESTS_ENVIRONMENT`, `TEST_LOG_COMPILER`. These names are build-system contracts rather than runtime C APIs.

Control flow: It defines `TESTS`, ships `.test` scripts and helper scripts, builds `libtestlookup.la` from passwd/group shims, and sets test environment variables such as PATH and locale.

State and persistence: State is persisted in generated build artifacts, installed files, test manifests, manual-page lists, or distribution tarballs. The file itself does not hold runtime process state.

Dependencies and integration points: Depends on the top-level Automake aggregation pattern, Autotools substitution variables, libtool build products, gettext/test environment conventions, and adjacent source files named by the fragment.

Risks: Omitting or misclassifying entries can drop headers, manpages, examples, tests, or tools from builds and release archives. Tool and test fragments also affect installed user-facing behavior and CI signal quality.

Test signals: Run `autoreconf -f -i`, `./configure`, `make`, `make check`, `make distcheck`, inspect installed headers/manpages/tools, and verify release tarballs include the listed documentation, examples, fixtures, and helper scripts.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/test/Makemodule.am -->
