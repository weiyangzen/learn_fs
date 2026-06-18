# sources/test-tools/syzkaller/syz-cluster/overlays/local/common/workflow-artifacts.yaml

## Purpose
Configures Argo's default artifact repository for local clusters.

## Important APIs, types, and functions
Defines `ConfigMap` `artifact-repositories` annotated as default artifact repository, with `gcs-repo` bucket `workflow-artifacts`.

## Control flow
Argo stores workflow artifacts in the fake GCS bucket initialized by `fake-gcs.yaml`.

## State and persistence behavior
Artifact state is stored in fake GCS backed by `emptyDir`, so it is ephemeral.

## Dependencies and integration points
Requires fake GCS service and executor `STORAGE_EMULATOR_HOST` patch.

## Risks and edge cases
Bucket name must match fake-gcs initialization. Artifacts disappear on fake-gcs pod restart.

## Test signals
Workflow runs in local cluster validate artifact upload/download.
