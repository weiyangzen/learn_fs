<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/doc/Makemodule.am -->
# sources/security-integrity/acl/doc/Makemodule.am

Purpose: Automake module that installs primary documentation (`CHANGES`, `COPYING`, LGPL notice, `INSTALL`, extension and library notes) and ships supplemental old/TODO documents in release archives. The file is 10 lines.

Important APIs and targets: Important declarations or variables include `dist_doc_DATA`, `EXTRA_DIST`. These names are build-system contracts rather than runtime C APIs.

Control flow: `dist_doc_DATA` and `EXTRA_DIST` are appended when the top-level `Makefile.am` includes this fragment, so `make install` and `make dist` carry the expected documentation set.

State and persistence: State is persisted in generated build artifacts, installed files, test manifests, manual-page lists, or distribution tarballs. The file itself does not hold runtime process state.

Dependencies and integration points: Depends on the top-level Automake aggregation pattern, Autotools substitution variables, libtool build products, gettext/test environment conventions, and adjacent source files named by the fragment.

Risks: Omitting or misclassifying entries can drop headers, manpages, examples, tests, or tools from builds and release archives. Tool and test fragments also affect installed user-facing behavior and CI signal quality.

Test signals: Run `autoreconf -f -i`, `./configure`, `make`, `make check`, `make distcheck`, inspect installed headers/manpages/tools, and verify release tarballs include the listed documentation, examples, fixtures, and helper scripts.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/doc/Makemodule.am -->
