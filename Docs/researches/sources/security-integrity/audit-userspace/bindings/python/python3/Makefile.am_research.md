<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/bindings/python/python3/Makefile.am -->
# sources/security-integrity/audit-userspace/bindings/python/python3/Makefile.am

Purpose: automake/libtool recipe for building the Python 3 `auparse` extension module.

Important build API: builds `auparse.la` from shared source `bindings/python/auparse_python.c`, with Python 3 CFLAGS/includes/libs, `-module -avoid-version`, relro linker flag, and dependencies on `libauparse.la` and `libaudit.la`.

Control flow and state: `check-local` probes `python3-config --embed --libs`, skips with code 77 if unavailable, then rebuilds with `-Wl,--no-undefined` to catch missing symbols.

Dependencies and integration: uses configured `PYTHON3_*` variables and top build libraries. Installed under Python `pyexec` extension location.

Risks and test signals: linking against the correct embed libs is platform-sensitive. The no-undefined check is a strong build-time signal for CPython/libaudit/libauparse linkage regressions.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/bindings/python/python3/Makefile.am -->
