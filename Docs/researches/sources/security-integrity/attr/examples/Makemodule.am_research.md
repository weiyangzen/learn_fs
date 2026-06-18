## sources/security-integrity/attr/examples/Makemodule.am

Purpose: distribution fragment for attr examples.

It ships `copyattr.c` and the standalone example `Makefile`. No runtime state. Dependencies are the top-level Automake `EXTRA_DIST`. Risks are examples drifting from installed headers if not compiled in regular CI. Test signal is `make dist` coverage and optional manual example build.
