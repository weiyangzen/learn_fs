<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/is_linux_mips_n64.c -->
# sources/test-tools/strace/tests/is_linux_mips_n64.c

Purpose: Minimal architecture probe used by the strace testsuite to report whether the current build is Linux MIPS n64.

Important APIs/types/functions: Uses preprocessor architecture checks, `printf`, and `SKIP_MAIN_UNDEFINED("MIPS")` for non-MIPS builds.

Control flow: On MIPS it prints a true/false style result based on ABI macros; on non-MIPS it compiles to a skip test.

State/persistence behavior: No runtime state beyond stdout.

Dependencies: Compiler-defined MIPS ABI macros and the strace test framework.

Integration points: Provides a small feature probe for tests that need MIPS n64-specific expectations.

Risks: Toolchain macro naming changes could misclassify the ABI.

Test signals: A simple printed result on MIPS or skip on other architectures.

Source read signal: complete file read for this research pass; file size 25 line(s), 368 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/is_linux_mips_n64.c -->
