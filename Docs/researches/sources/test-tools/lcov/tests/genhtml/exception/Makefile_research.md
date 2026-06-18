<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/exception/Makefile -->
# sources/test-tools/lcov/tests/genhtml/exception/Makefile

- Purpose: Makefile entry for `exception.sh` in the lcov test harness.
- Important APIs/types/functions: Defines `TESTS` and `clean`; no functions or types.
- Control flow: Common make rules run the listed test(s); clean delegates to `local clean target`.
- State and persistence behavior: Only make variables persist; generated files are owned by child scripts.
- Dependencies and integration points: Depends on the nearby `common.mak` include and executable test scripts.
- Risks: Risk is stale cleanup coverage if generated artifact names change.
- Test signals: Passing signal is successful recursive make execution and clean completion.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/exception/Makefile -->
