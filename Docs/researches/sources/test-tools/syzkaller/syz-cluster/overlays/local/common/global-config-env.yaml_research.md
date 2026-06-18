# sources/test-tools/syzkaller/syz-cluster/overlays/local/common/global-config-env.yaml

## Purpose
Provides local environment variables for Spanner emulator and fake GCS.

## Important APIs, types, and functions
Defines `ConfigMap` `global-config-env` with `SPANNER_EMULATOR_HOST`, `SPANNER_DATABASE_URI`, `STORAGE_EMULATOR_HOST`, and `BLOB_STORAGE_GCS_BUCKET`.

## Control flow
Local pods read these values so app environment connects to in-cluster emulators instead of cloud services.

## State and persistence behavior
No state; points apps to ephemeral local services.

## Dependencies and integration points
Requires `cloud-spanner-emulator` and `fake-gcs-server` services from local common overlay.

## Risks and edge cases
Hard-coded fake project/instance/database names must align with migration tooling. Bucket name must match fake-gcs init-created directory.

## Test signals
Local cluster smoke migration/startup validates the values.
