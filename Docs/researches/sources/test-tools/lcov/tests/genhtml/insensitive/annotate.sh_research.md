<!-- BEGIN_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/insensitive/annotate.sh -->
# sources/test-tools/lcov/tests/genhtml/insensitive/annotate.sh

- Purpose: Perl case-insensitive annotation callback used by genhtml tests to provide source line metadata and modification timestamps.
- Important APIs/types/functions: Defines `get_modify_time`; uses `POSIX::strftime` and, in the insensitive variant, path case matching helpers/modules.
- Control flow: Resolves the requested file, calculates modification time, reads source lines, normalizes carriage returns, and emits annotation records for genhtml.
- State and persistence behavior: Reads filesystem metadata and file contents; writes no persistent files except caller-controlled logs.
- Dependencies and integration points: Depends on Perl modules, file stat data, and genhtml annotate callback protocol.
- Risks: Timestamp and path-case sensitivity can affect version/annotation consistency checks.
- Test signals: Passing signals are expected annotation/owner/date data in generated reports or expected annotation failure diagnostics.
<!-- END_FILE_RESEARCH: sources/test-tools/lcov/tests/genhtml/insensitive/annotate.sh -->
