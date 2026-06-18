# sources/test-tools/syzkaller/syz-cluster/overlays/local/common/patch-workflow-controller-configmap.yaml

## Purpose
Adds fake GCS emulator environment to Argo executor configuration for local clusters.

## Important APIs, types, and functions
Patches `ConfigMap` `workflow-controller-configmap` in namespace `argo`, setting `data.executor` to include environment variable `STORAGE_EMULATOR_HOST=http://fake-gcs-server.default.svc.cluster.local:4443`.

## Control flow
Argo executor pods inherit this environment so artifact handling targets fake GCS.

## State and persistence behavior
No state directly; redirects workflow artifact IO to ephemeral fake GCS.

## Dependencies and integration points
Depends on fake-gcs service and Argo controller config semantics. Used together with local `workflow-artifacts.yaml`.

## Risks and edge cases
ConfigMap data replacement must coexist with other Argo config patches; replacing `data.executor` incorrectly can drop other executor settings. YAML indentation inside string is significant.

## Test signals
Workflow artifact behavior in local runs validates this.
