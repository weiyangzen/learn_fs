<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auplugin/test/fgets_test.c -->
# sources/security-integrity/audit-userspace/auplugin/test/fgets_test.c

Purpose: unit test for the global `auplugin_fgets` API.

Important APIs and functions: `test_simple_line`, `test_multiple_lines`, `test_partial_line`, and `test_long_line` cover `auplugin_fgets_clear`, `auplugin_fgets_more`, `auplugin_fgets_eof`, and `auplugin_fgets`.

Control flow and state: each test creates a pipe, clears global state, writes known input, closes the writer, reads expected chunks, and closes the reader. Long-line testing verifies that output is clamped to `blen - 1`, leftover data remains detectable, and EOF is only set after an additional read.

Dependencies and integration: depends on POSIX pipes and the installed auplugin header. It is run by the auplugin test Makefile.

Risks and test signals: valuable for global-state regressions but cannot validate concurrent use because the global API is intentionally single-state. Passing prints `audit-fgets tests: all passed`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auplugin/test/fgets_test.c -->
