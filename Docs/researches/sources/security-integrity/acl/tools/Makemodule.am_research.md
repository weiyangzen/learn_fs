<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/tools/Makemodule.am -->
# sources/security-integrity/acl/tools/Makemodule.am

Purpose: Automake module building installed ACL tools `chacl`, `getfacl`, and `setfacl` plus parser/sequence/set helper code. The file is 23 lines.

Important APIs and targets: Important declarations or variables include `tools_ldadd`, `bin_PROGRAMS`, `chacl_SOURCES`, `chacl_LDADD`, `getfacl_SOURCES`, `getfacl_LDADD`, `setfacl_SOURCES`, `setfacl_LDADD`. These names are build-system contracts rather than runtime C APIs.

Control flow: It appends programs to `bin_PROGRAMS`, enumerates per-tool source lists, and links tools with libacl/libmisc/gettext dependencies inherited from the top-level build.

State and persistence: State is persisted in generated build artifacts, installed files, test manifests, manual-page lists, or distribution tarballs. The file itself does not hold runtime process state.

Dependencies and integration points: Depends on the top-level Automake aggregation pattern, Autotools substitution variables, libtool build products, gettext/test environment conventions, and adjacent source files named by the fragment.

Risks: Omitting or misclassifying entries can drop headers, manpages, examples, tests, or tools from builds and release archives. Tool and test fragments also affect installed user-facing behavior and CI signal quality.

Test signals: Run `autoreconf -f -i`, `./configure`, `make`, `make check`, `make distcheck`, inspect installed headers/manpages/tools, and verify release tarballs include the listed documentation, examples, fixtures, and helper scripts.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/tools/Makemodule.am -->
