# sources/storage-engines/pebble/.github/workflows/nightly-code-cover.yaml

## Purpose
`nightly-code-cover.yaml` manually generates and publishes full repository code coverage to Google Cloud Storage.

## Important APIs, types, and functions
It uses `actions/checkout`, `actions/setup-go`, `scripts/code-coverage.sh`, installs `lcov` through apt, authenticates with `CODECOVER_SERVICE_ACCOUNT_KEY`, sets up `gcloud`, and runs `scripts/code-coverage-publish.sh`.

## Control flow
On manual dispatch, the workflow checks out with full history, installs Go 1.26, generates coverage, installs lcov, authenticates to GCP, sets up the Cloud SDK, and publishes coverage.

## State and persistence behavior
Coverage reports are generated locally and then persisted to a GCS destination selected by the publish script. Repository state is not intentionally changed.

## Dependencies and integration points
It integrates repository coverage scripts with GCS and likely external coverage viewers. It depends on apt, lcov, GCP credentials, and Cloud SDK availability.

## Risks and edge cases
The checkout references `github.event.pull_request.head.sha`, which is not defined for `workflow_dispatch`; this may resolve empty or fail depending on GitHub expression handling. Manual full-coverage runs require secrets and can fail if GCP actions versions or credentials change.

## Test signals
Signals include successful coverage script output, lcov installation, GCP auth, and publish script completion with expected remote coverage artifacts.
