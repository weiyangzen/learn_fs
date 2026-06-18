<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/extract/brokenCallback.pm -->
# sources/test-tools/lcov/tests/lcov/extract/brokenCallback.pm

- Purpose: Perl callback fixture for negative or specialized lcov/genhtml callback-path testing in `sources/test-tools/lcov/tests/lcov/extract`.
- Important APIs/types/functions: Defines package `brokenCallback` with methods: new, resolve.
- Control flow: The harness loads it through lcov/genhtml callback options so selected methods either provide synthetic data or deliberately fail to validate diagnostics.
- State and persistence behavior: State is held in blessed constructor arguments where present; modules write no persistent files themselves.
- Dependencies and integration points: Depends on Perl callback loading and the lcov/genhtml callback protocol; integrated by nearby shell tests.
- Risks: API drift in callback method names or diagnostic formatting can change the targeted failure mode.
- Test signals: Passing signal is the parent shell script observing the expected callback result, warning, or failure message.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/lcov/extract/brokenCallback.pm -->
