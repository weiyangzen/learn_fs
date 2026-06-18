<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/auparse_test.ref.py -->
# sources/security-integrity/audit-userspace/auparse/test/auparse_test.ref.py

Purpose: expected stdout transcript for `auparse_test.py`. It is a golden file, not executable code, but it defines the externally observed behavior of the Python auparse binding tests.

Important content: the file records every test heading, parsed event/record/field summary, interpreted value, search result, feed callback traversal, long-record walk, descriptor-source status, and file-pointer status. It captures the expected Python rendering of `None` as normalized by the test script, event timestamps, type names, line numbers, filenames, and audit field values.

Control flow and state: no runtime state is stored here. The shell harness regenerates current output from `auparse_test.py`, normalizes source paths with `sed`, and diffs the result against this file. The reference therefore persists a snapshot of parser and binding behavior.

Dependencies and integration: tightly coupled to `auparse_test.py`, fixture logs, the C extension, libaudit interpretation tables, and the shell wrapper. Any intended output change requires a coordinated update to both test logic and reference.

Risks and test signals: high signal for regressions in formatting, cursor order, field interpretation, descriptor lifetime, and source path handling; low diagnostic quality because any diff can be large. The risk is false positives from benign output wording changes or platform-specific interpretation differences.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/auparse_test.ref.py -->
