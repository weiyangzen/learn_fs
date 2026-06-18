<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/run_auparselol_test.sh.in -->
# sources/security-integrity/audit-userspace/auparse/test/run_auparselol_test.sh.in

Purpose: minimal shell harness dedicated to `auparselol_test` raw reconstruction.

Important behavior: runs `./auparselol_test -f "$srcdir"/test3.log --check`, sorts output into `auparse_test.cur`, transforms the fixture with `auditd_raw.sed` into `auparse_test.raw`, and diffs both files.

Control flow and state: `set -e` makes any command failure fatal. It writes two local temporary comparison files and reads only configured `srcdir`.

Dependencies and integration: depends on the compiled `auparselol_test`, fixture `test3.log`, and sed script. It is useful as a narrower check than the full auparse suite.

Risks and test signals: verifies feed parsing and raw output reconstruction, but because both sides are sorted it ignores original event order. Diff success is the pass signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/run_auparselol_test.sh.in -->
