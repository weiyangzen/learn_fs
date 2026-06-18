# sources/storage-engines/badger/.github/workflows/ci-badger-bank-tests.yml

Purpose: pull-request and manual CI for a shorter Badger bank invariant test.

Important flow: on PRs to `main` or `release/v*` excluding docs/images, it checks out code, sets up Go, installs dependencies and jemalloc, installs the race-enabled Badger CLI, creates a `bank` directory, and runs `badger bank test -v --dir=. -d=20m`.

State and persistence: test state is a temporary database under `bank`; no artifacts are configured. Dependencies are the Makefile dependency and jemalloc targets, Badger CLI install, race detector, and GitHub Ubuntu runner. Risks: verbose bank logging can be noisy, the test duration is significant for PR feedback, and it does not run the optional stream/subscriber bank checks. Test signals are transaction invariant failures, race detector failures, and workflow timing.
