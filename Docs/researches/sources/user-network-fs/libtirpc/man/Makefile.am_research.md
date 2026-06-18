<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/man/Makefile.am -->
# sources/user-network-fs/libtirpc/man/Makefile.am

Purpose: Automake rules for libtirpc manual page installation and distribution.

Important APIs, types, and functions: Defines `dist_man_MANS`, conditional GSS man pages, and extra distributed man pages.

Control flow: Automake installs base man pages and adds GSS-specific pages when configured.

State and persistence behavior: No runtime state.

Dependencies and integration points: Depends on `GSS` conditional from configure and manpage source files.

Risks: Manual page list can drift from installed APIs; conditional docs must match optional features.

Test signals: Dist/install checks provide signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/man/Makefile.am -->
