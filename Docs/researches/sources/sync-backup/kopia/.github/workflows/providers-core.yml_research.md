# sources/sync-backup/kopia/.github/workflows/providers-core.yml

## Purpose
Runs cloud and remote storage provider integration tests for core backends: Azure, GCS, S3, and SFTP. It is scheduled daily, runs on pushes to `master`, `test/providers`, and version tags, and supports manual dispatch.

## APIs, Control Flow, and Integration Points
The job is guarded to `kopia/kopia` and non-fork pull request contexts. It checks out the requested ref expression, installs Go, runs `make provider-tests-deps`, then runs `make provider-tests` with `PROVIDER_TEST_TARGET` values. Provider credentials are injected per step via repository secrets. Later provider steps use `if: success() || failure()`, so a failure in Azure does not prevent GCS, S3, and SFTP from running.

## State, Persistence, and Dependencies
External persistent state exists in cloud buckets, immutable containers, S3-compatible endpoints, and any SFTP test service. Local state includes downloaded provider test tooling such as rclone and minio client. No artifacts are uploaded.

## Risks and Test Signals
The ref expression uses `github.event.inputs.ref_name || github.ref`, while the dispatch input is named `ref`; this may prevent manual selection from working as intended. Secret availability and external service flakiness can dominate results. The signal is high value because it exercises real provider implementations under `repo/blob/<target>` using the same Makefile target and environment variables used by developers.
