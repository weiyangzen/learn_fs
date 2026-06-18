<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/doc/Makefile.am -->
# sources/user-network-fs/libtirpc/doc/Makefile.am

Purpose: Automake rules for installing libtirpc documentation files.

Important APIs, types, and functions: Lists `new_api` and conditionally `bindresvport.blacklist` when IPv6 is disabled, plus `EXTRA_DIST`.

Control flow: Automake includes docs in distributions and installs configured doc data.

State and persistence behavior: No runtime state.

Dependencies and integration points: Depends on `INET6` conditional from configure.

Risks: Conditional documentation install can surprise packagers expecting a stable doc file set.

Test signals: Build/distcheck signals only.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/doc/Makefile.am -->
