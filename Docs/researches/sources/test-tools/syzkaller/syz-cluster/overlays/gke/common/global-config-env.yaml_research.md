# sources/test-tools/syzkaller/syz-cluster/overlays/gke/common/global-config-env.yaml

## Purpose
Provides environment variable config entries for GKE deployments.

## Important APIs, types, and functions
Defines `ConfigMap` `global-config-env` with `SPANNER_DATABASE_URI` and `BLOB_STORAGE_GCS_BUCKET` values substituted from `${SPANNER_DATABASE_URI}` and `${BLOB_STORAGE_GCS_BUCKET}`.

## Control flow
Kustomize/render tooling substitutes environment-specific values before deployment; pods consume the config map through their app environment setup.

## State and persistence behavior
No persistence itself; points services at durable Cloud Spanner and GCS resources.

## Dependencies and integration points
Used by GKE common overlay and application config loading.

## Risks and edge cases
Unsubstituted placeholders would deploy invalid config. Secrets are not handled here; bucket/database names are non-secret but environment-specific.

## Test signals
Runtime startup failures would reveal bad values. No direct unit test.
