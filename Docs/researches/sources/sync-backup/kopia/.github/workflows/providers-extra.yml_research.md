# sources/sync-backup/kopia/.github/workflows/providers-extra.yml

## Purpose
Runs integration tests for less central providers: B2, Google Drive, Rclone, and WebDAV. It is scheduled twice weekly, runs on `test/providers` and version tags, and supports manual dispatch.

## APIs, Control Flow, and Integration Points
The workflow mirrors the core provider lane: checkout, Go setup, `make provider-tests-deps`, then sequential `make provider-tests PROVIDER_TEST_TARGET=...` invocations with provider-specific secrets. Each provider step after setup uses `if: success() || failure()` to collect as many independent provider results as possible in one run.

## State, Persistence, and Dependencies
It depends on external provider accounts, buckets, folders, WebDAV credentials, and rclone configuration supplied by secrets. Test tooling is prepared by the Makefile, and no log artifacts are explicitly persisted.

## Risks and Test Signals
Like the core provider workflow, checkout references `github.event.inputs.ref_name` even though the dispatch input is `ref`, which is a likely manual-dispatch bug. Provider credentials and remote service rate limits are operational risks. The test signal is narrower than core providers but important for compatibility with optional storage targets and rclone-backed repositories.
