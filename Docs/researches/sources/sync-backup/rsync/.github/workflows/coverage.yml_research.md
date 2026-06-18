# sources/sync-backup/rsync/.github/workflows/coverage.yml

Purpose: generate gcov/gcovr coverage reports on Ubuntu.

Important APIs/types/functions: installs coverage-capable dependencies, configures with coverage flags, runs `make coverage` and `make coverage-tcp`, extracts line/function/branch/decision summaries, and uploads HTML reports.

Control flow: triggered weekly and on relevant push/PR changes. The Makefile handles gcda cleanup, parallel test execution, report directories, and gcovr exclusions for vendored code.

State and persistence: uploads `coverage-html` artifact with `coverage` and `coverage-tcp` directories retained 45 days.

Dependencies/integration: integrates Makefile coverage targets, gcovr, gcc coverage instrumentation, and the test suite.

Risks: coverage data can be toolchain-sensitive; failed tests still produce reports but should fail the job through Makefile exit propagation.

Test signals: gcovr summaries and HTML artifacts for default and TCP transports.
