<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/bindings/swig/src/Makefile.am -->
# sources/security-integrity/audit-userspace/bindings/swig/src/Makefile.am

Purpose: distribution-only automake file for the SWIG interface source directory.

Important build API: lists `auditswig.i` in `EXTRA_DIST` and cleanup patterns.

Control flow and state: no compiled targets are declared here. The language-specific subdir references this interface file to generate wrappers.

Dependencies and integration: ensures `auditswig.i` is included in release tarballs for downstream SWIG wrapper generation.

Risks and test signals: low runtime risk, but omitting the interface would break distributed builds. Test signal is packaging/build success in `swig/python3`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/bindings/swig/src/Makefile.am -->
