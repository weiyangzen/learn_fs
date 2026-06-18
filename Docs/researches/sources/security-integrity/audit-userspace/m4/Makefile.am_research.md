# sources/security-integrity/audit-userspace/m4/Makefile.am

Purpose: Automake packaging fragment for project m4 macros.

Important APIs/types: sets `CONFIG_CLEAN_FILES`, installs `audit.m4` into `$(datadir)/aclocal` through `dist_m4data_DATA`.

Control flow: build-system only; no runtime behavior.

State and persistence: affects distribution and install artifacts, not program state.

Dependencies and integration: used by the Autotools build so downstream builds can consume audit's aclocal macro.

Risks and test signals: missing `audit.m4` in distribution can break dependent builds. Validation is Automake distribution/install checks rather than runtime tests.
