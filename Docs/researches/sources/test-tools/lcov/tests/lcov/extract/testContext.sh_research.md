<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/extract/testContext.sh -->
# sources/test-tools/lcov/tests/lcov/extract/testContext.sh

- Purpose: Shell context callback that emits user and multiline context data or fails deliberately.
- Important APIs/types/functions: If first arg is `die`, prints `dying` and exits 1; otherwise prints `USERNAME` and three `MULTILINE` records.
- Control flow: Used through `--context` to validate shell callback parsing, failure handling, and `--ignore callback`.
- State and persistence behavior: Reads current user via `whoami`; writes context records to stdout.
- Dependencies and integration points: Depends on `/bin/sh`, `whoami`, and lcov context parsing.
- Risks: Username/environment variance can affect exact context content.
- Test signals: Passing signals are context JSON/comment fields and expected failure/ignored-failure behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/extract/testContext.sh -->
