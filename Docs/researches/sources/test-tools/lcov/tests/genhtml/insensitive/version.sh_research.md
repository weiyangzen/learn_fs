<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/insensitive/version.sh -->
# sources/test-tools/lcov/tests/genhtml/insensitive/version.sh

- Purpose: Minimal version callback returning a stable version for case-insensitive path tests.
- Important APIs/types/functions: Executable Perl callback prints `1` and exits 0.
- Control flow: Ignores input and returns a constant version so path-case behavior is isolated from real VCS state.
- State and persistence behavior: No state is read or written.
- Dependencies and integration points: Depends only on Perl and version-script callback invocation.
- Risks: Constant versions can hide path-specific version behavior, intentionally.
- Test signals: Passing signal is stable version comparison across differently cased paths.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/insensitive/version.sh -->
