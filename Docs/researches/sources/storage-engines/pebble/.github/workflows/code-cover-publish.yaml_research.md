# sources/storage-engines/pebble/.github/workflows/code-cover-publish.yaml

## Purpose
`code-cover-publish.yaml` publishes PR coverage artifacts from the untrusted generation workflow to a public GCS bucket using repository secrets in a separate trusted workflow.

## Important APIs, types, and functions
It triggers on completed `workflow_run` events for `PR code coverage (generate)`. The job uses `actions/download-artifact`, `google-github-actions/auth`, and `google-github-actions/upload-cloud-storage`.

## Control flow
The job runs only when the source workflow was a pull request and concluded successfully. It downloads the `cover` artifact from the triggering run using the run ID, authenticates to Google Cloud with `CODECOVER_SERVICE_ACCOUNT_KEY`, and uploads `cover-*.json` files to `crl-codecover-public/pr-pebble/`.

## State and persistence behavior
The workflow writes coverage JSON objects into GCS. It does not mutate repository state.

## Dependencies and integration points
It is paired with `code-cover-gen.yaml`, uses GitHub artifact storage as the handoff boundary, and integrates with Reviewable or other consumers reading the public bucket.

## Risks and edge cases
Secrets are exposed only to this trusted workflow, but artifact content originated from untrusted PR code. The upload action must treat files as inert data. Missing artifacts or expired runs cause publish failures.

## Test signals
Signals include correct filtering of workflow_run events, successful artifact download by run ID, GCP authentication, and expected objects in the destination bucket.
