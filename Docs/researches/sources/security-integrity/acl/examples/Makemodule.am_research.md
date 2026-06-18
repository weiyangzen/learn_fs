<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/examples/Makemodule.am -->
# sources/security-integrity/acl/examples/Makemodule.am

Purpose: Automake module that ships example programs and example README material with distribution archives without making them installed tools. The file is 7 lines.

Important APIs and targets: Important declarations or variables include `EXTRA_DIST`. These names are build-system contracts rather than runtime C APIs.

Control flow: The top-level makefile includes this fragment and `EXTRA_DIST` picks up example C sources, README, and example-local make metadata for release packaging.

State and persistence: State is persisted in generated build artifacts, installed files, test manifests, manual-page lists, or distribution tarballs. The file itself does not hold runtime process state.

Dependencies and integration points: Depends on the top-level Automake aggregation pattern, Autotools substitution variables, libtool build products, gettext/test environment conventions, and adjacent source files named by the fragment.

Risks: Omitting or misclassifying entries can drop headers, manpages, examples, tests, or tools from builds and release archives. Tool and test fragments also affect installed user-facing behavior and CI signal quality.

Test signals: Run `autoreconf -f -i`, `./configure`, `make`, `make check`, `make distcheck`, inspect installed headers/manpages/tools, and verify release tarballs include the listed documentation, examples, fixtures, and helper scripts.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/examples/Makemodule.am -->
