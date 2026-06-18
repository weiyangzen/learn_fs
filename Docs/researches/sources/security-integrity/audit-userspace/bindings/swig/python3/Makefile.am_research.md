<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/bindings/swig/python3/Makefile.am -->
# sources/security-integrity/audit-userspace/bindings/swig/python3/Makefile.am

Purpose: automake/libtool recipe for generating and building the Python 3 SWIG `_audit` module plus `audit.py`.

Important build API: sets SWIG flags/includes, builds `_audit.la` from generated `audit_wrap.c`, installs `audit.py`, links against `libaudit.la` and Python libs, and regenerates outputs from `../src/auditswig.i`.

Control flow and state: `check-local` performs the same `python3-config --embed --libs` probe/skip and no-undefined rebuild pattern as the handwritten Python binding. `CLEANFILES` removes generated SWIG artifacts.

Dependencies and integration: depends on SWIG, Python headers/libs, libaudit, and `audit_logging.h`. Its built shared object is copied by the auparse shell harness so Python tests can import audit support.

Risks and test signals: generated-file drift, SWIG version differences, and Python embed linker flags are main risks. No-undefined check gives symbol coverage; Python harness import gives runtime packaging coverage.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/bindings/swig/python3/Makefile.am -->
