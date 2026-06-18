<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auplugin/test/Makefile.am -->
# sources/security-integrity/audit-userspace/auplugin/test/Makefile.am

Purpose: automake test definition for `libauplugin`.

Important build API: builds `fgets_test`, `metrics_test`, and `fgets_r_test`, registers all as `TESTS`, includes auplugin/lib/auparse headers, and links each program against `../libauplugin.la`. ASAN flags are conditionally appended.

Control flow and state: no runtime logic; automake compiles and runs the three binaries during `make check`.

Dependencies and integration: depends on the local auplugin library and project warning flags. `fgets_r_test` also uses fixture data from the auparse test tree at runtime through `srcdir`.

Risks and test signals: missing `srcdir` propagation or link dependencies can break tests. ASAN integration increases memory-error signal when configured.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auplugin/test/Makefile.am -->
