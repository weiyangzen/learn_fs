<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/bindings/swig/Makefile.am -->
# sources/security-integrity/audit-userspace/bindings/swig/Makefile.am

Purpose: top-level automake coordinator for SWIG-generated audit bindings.

Important build API: distributes `src/auditswig.i`, always descends into `src`, and conditionally descends into `python3` when `USE_PYTHON3` is enabled.

Control flow and state: no direct build logic besides subdirectory selection and cleanup patterns.

Dependencies and integration: ties the SWIG interface file to language-specific generated bindings. The Python auparse shell test also locates the built SWIG `_audit*.so` module.

Risks and test signals: stale SWIG interface distribution or disabled Python 3 condition can break downstream binding tests. Actual compile/test signals live in `swig/python3`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/bindings/swig/Makefile.am -->
