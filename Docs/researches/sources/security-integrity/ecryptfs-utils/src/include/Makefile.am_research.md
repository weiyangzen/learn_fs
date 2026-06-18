# sources/security-integrity/ecryptfs-utils/src/include/Makefile.am

Purpose: installs public and private headers.

Important APIs/targets: `include_HEADERS = ecryptfs.h`; `dist_noinst_HEADERS = decision_graph.h`.

Control flow/state: public API header is installed; decision graph header is distributed but not installed.

Dependencies/integration: used by libecryptfs, utilities, daemon, key modules, and SWIG wrapper.

Risks: exposing `ecryptfs.h` means ABI/API compatibility matters. `decision_graph.h` remains internal but is shared across source subdirs.

Test signals: install checks and downstream compile.
