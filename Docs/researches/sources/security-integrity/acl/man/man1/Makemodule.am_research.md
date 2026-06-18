<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/man/man1/Makemodule.am -->
# sources/security-integrity/acl/man/man1/Makemodule.am

Purpose: Automake module adding command manual pages for installed ACL tools. The file is 4 lines.

Important APIs and targets: Important declarations or variables include `dist_man_MANS`. These names are build-system contracts rather than runtime C APIs.

Control flow: It appends `chacl.1`, `getfacl.1`, and `setfacl.1` to manpage distribution/install variables so tool documentation follows tool installation.

State and persistence: State is persisted in generated build artifacts, installed files, test manifests, manual-page lists, or distribution tarballs. The file itself does not hold runtime process state.

Dependencies and integration points: Depends on the top-level Automake aggregation pattern, Autotools substitution variables, libtool build products, gettext/test environment conventions, and adjacent source files named by the fragment.

Risks: Omitting or misclassifying entries can drop headers, manpages, examples, tests, or tools from builds and release archives. Tool and test fragments also affect installed user-facing behavior and CI signal quality.

Test signals: Run `autoreconf -f -i`, `./configure`, `make`, `make check`, `make distcheck`, inspect installed headers/manpages/tools, and verify release tarballs include the listed documentation, examples, fixtures, and helper scripts.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/man/man1/Makemodule.am -->
