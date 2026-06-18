<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/man/man3/Makemodule.am -->
# sources/security-integrity/acl/man/man3/Makemodule.am

Purpose: Automake module adding section 3 API manual pages for libacl functions. The file is 40 lines.

Important APIs and targets: Important declarations or variables include `dist_man_MANS`. These names are build-system contracts rather than runtime C APIs.

Control flow: It enumerates public ACL API pages for permissions, entries, serialization, file/fd access, validation, text formatting, and extension helpers, keeping installed API docs aligned with exported symbols.

State and persistence: State is persisted in generated build artifacts, installed files, test manifests, manual-page lists, or distribution tarballs. The file itself does not hold runtime process state.

Dependencies and integration points: Depends on the top-level Automake aggregation pattern, Autotools substitution variables, libtool build products, gettext/test environment conventions, and adjacent source files named by the fragment.

Risks: Omitting or misclassifying entries can drop headers, manpages, examples, tests, or tools from builds and release archives. Tool and test fragments also affect installed user-facing behavior and CI signal quality.

Test signals: Run `autoreconf -f -i`, `./configure`, `make`, `make check`, `make distcheck`, inspect installed headers/manpages/tools, and verify release tarballs include the listed documentation, examples, fixtures, and helper scripts.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/man/man3/Makemodule.am -->
