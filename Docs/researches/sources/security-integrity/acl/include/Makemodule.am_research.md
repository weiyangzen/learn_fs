<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/include/Makemodule.am -->
# sources/security-integrity/acl/include/Makemodule.am

Purpose: Automake module listing public and private headers for distribution and installation under the generated `include/sys` and `include/acl` compatibility directories. The file is 24 lines.

Important APIs and targets: Important declarations or variables include module variables listed in the file. These names are build-system contracts rather than runtime C APIs.

Control flow: The header variables are consumed after `configure` creates include-directory symlinks, ensuring installed `sys/acl.h`, `acl/libacl.h`, and internal helper headers are available to library/tool builds.

State and persistence: State is persisted in generated build artifacts, installed files, test manifests, manual-page lists, or distribution tarballs. The file itself does not hold runtime process state.

Dependencies and integration points: Depends on the top-level Automake aggregation pattern, Autotools substitution variables, libtool build products, gettext/test environment conventions, and adjacent source files named by the fragment.

Risks: Omitting or misclassifying entries can drop headers, manpages, examples, tests, or tools from builds and release archives. Tool and test fragments also affect installed user-facing behavior and CI signal quality.

Test signals: Run `autoreconf -f -i`, `./configure`, `make`, `make check`, `make distcheck`, inspect installed headers/manpages/tools, and verify release tarballs include the listed documentation, examples, fixtures, and helper scripts.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/include/Makemodule.am -->
