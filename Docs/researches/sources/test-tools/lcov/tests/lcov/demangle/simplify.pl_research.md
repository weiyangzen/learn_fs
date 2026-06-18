<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/demangle/simplify.pl -->
# sources/test-tools/lcov/tests/lcov/demangle/simplify.pl

- Purpose: Small Perl helper script used by adjacent lcov/genhtml tests.
- Important APIs/types/functions: No reusable package API unless explicitly declared; executable behavior is line/argument oriented.
- Control flow: The parent harness invokes it as a callback/filter/helper and validates transformed output or diagnostics.
- State and persistence behavior: Usually streams stdin/stdout or prints a simple value; no standalone persistence.
- Dependencies and integration points: Depends on Perl and lcov/genhtml helper callback contracts.
- Risks: Regex or argument protocol changes can alter behavior.
- Test signals: Passing signal is the adjacent shell test observing the expected transformed names, records, or helper output.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/demangle/simplify.pl -->
