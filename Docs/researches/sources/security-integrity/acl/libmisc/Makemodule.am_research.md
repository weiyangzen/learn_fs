<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libmisc/Makemodule.am -->
# sources/security-integrity/acl/libmisc/Makemodule.am

Purpose: Automake module that builds the internal `libmisc.la` convenience library used by libacl and command-line tools. The file is 9 lines.

Important APIs and targets: Important declarations or variables include `noinst_LTLIBRARIES`, `libmisc_la_SOURCES`. These names are build-system contracts rather than runtime C APIs.

Control flow: It appends `libmisc.la` to non-installed libtool libraries and lists helper sources for allocation growth, line parsing, quoting, uid/gid lookup, unquoting, and directory traversal.

State and persistence: State is persisted in generated build artifacts, installed files, test manifests, manual-page lists, or distribution tarballs. The file itself does not hold runtime process state.

Dependencies and integration points: Depends on the top-level Automake aggregation pattern, Autotools substitution variables, libtool build products, gettext/test environment conventions, and adjacent source files named by the fragment.

Risks: Omitting or misclassifying entries can drop headers, manpages, examples, tests, or tools from builds and release archives. Tool and test fragments also affect installed user-facing behavior and CI signal quality.

Test signals: Run `autoreconf -f -i`, `./configure`, `make`, `make check`, `make distcheck`, inspect installed headers/manpages/tools, and verify release tarballs include the listed documentation, examples, fixtures, and helper scripts.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libmisc/Makemodule.am -->
