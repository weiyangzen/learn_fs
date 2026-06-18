<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/bindings/python/Makefile.am -->
# sources/security-integrity/audit-userspace/bindings/python/Makefile.am

Purpose: automake coordinator for the handwritten Python auparse binding.

Important build API: distributes `auparse_python.c`, sets cleanup patterns, and conditionally descends into `python3` when `USE_PYTHON3` is enabled.

Control flow and state: no direct compilation here; build work is delegated to `bindings/python/python3/Makefile.am`.

Dependencies and integration: connects the source file to the Python 3 extension build. It intentionally has no Python 2 subdir in this tree.

Risks and test signals: risk is configuration mismatch where Python support is expected but `USE_PYTHON3` is false. Direct test signal comes from the python3 subdir and auparse shell harness.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/bindings/python/Makefile.am -->
