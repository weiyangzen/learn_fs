# sources/test-tools/syzkaller/syz-cluster/overlays/gke/common/workflow-artifacts.yaml

## Purpose
Configures Argo's default artifact repository for GKE.

## Important APIs, types, and functions
Defines `ConfigMap` `artifact-repositories` annotated with `workflows.argoproj.io/default-artifact-repository: gcs-repo`. The `gcs-repo` entry points to GCS bucket `${WORKFLOW_ARTIFACTS_BUCKET}`.

## Control flow
Argo workflows use this default artifact repository for artifact storage unless overridden.

## State and persistence behavior
Artifact state is persisted in the configured GCS bucket.

## Dependencies and integration points
Requires Argo controller config support, GCS bucket existence, and service account permissions.

## Risks and edge cases
Unsubstituted or missing bucket values break workflow artifacts. The config has no key/credential detail, so it relies on workload identity/service account setup.

## Test signals
Workflow artifact upload/download runtime behavior validates it.
