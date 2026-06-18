<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/bindings/Makefile.am -->
# sources/security-integrity/audit-userspace/bindings/Makefile.am

Purpose: top-level automake dispatcher for language bindings.

Important build API: sets cleanup patterns and declares `SUBDIRS = python golang swig`.

Control flow and state: automake descends into each binding implementation during build, install, dist, and check phases according to each subdirectory's conditions.

Dependencies and integration: links the project binding surface into the main build without itself compiling code. It coordinates the handwritten Python auparse binding, Go libaudit wrapper, and SWIG audit binding.

Risks and test signals: build failure in any enabled binding subdirectory can fail the aggregate binding step. There is no direct runtime test signal in this file.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/bindings/Makefile.am -->
