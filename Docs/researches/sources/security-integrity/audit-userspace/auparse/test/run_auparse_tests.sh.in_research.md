<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/run_auparse_tests.sh.in -->
# sources/security-integrity/audit-userspace/auparse/test/run_auparse_tests.sh.in

Purpose: automake-time shell harness for the auparse C and Python test suite.

Important behavior: copies fixture logs when running out of tree, runs `./auparse_test` and diffs stdout against `auparse_test.ref`, runs `./auparselol_test -f test3.log --check` and compares sorted reconstructed raw output with `auditd_raw.sed`, optionally locates and copies the built SWIG `_audit*.so`, then runs `auparse_test.py` with local Python and library paths and diffs against `auparse_test.ref.py`. It finishes with `./lookup_test`.

Control flow and state: `set -e` stops on the first failing command. Generated intermediates are `auparse_test.cur` and `auparse_test.raw`. Python execution is conditional on configured `use_python3`.

Dependencies and integration: uses configured `@srcdir@`, `@top_builddir@`, and `@use_python3@`. It depends on built auparse binaries, SWIG audit module, Python auparse module, fixture logs, sed scripts, and local shared libraries.

Risks and test signals: strong end-to-end diff gate, but path and shared-library discovery can fail before parser behavior is tested. The comment notes `databuf_test` is built but not run here.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/run_auparse_tests.sh.in -->
