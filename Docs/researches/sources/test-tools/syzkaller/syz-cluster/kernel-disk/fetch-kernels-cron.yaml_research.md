# sources/test-tools/syzkaller/syz-cluster/kernel-disk/fetch-kernels-cron.yaml

## Purpose
Schedules periodic kernel repository fetching through Argo Workflows.

## Important APIs, types, and functions
Defines an Argo `CronWorkflow` named `fetch-kernels-cron`, scheduled at `0 */8 * * *`, with `concurrencyPolicy: Replace`, `startingDeadlineSeconds: 0`, and a workflow template reference to `fetch-kernels-workflow-template`.

## Control flow
Argo starts the referenced workflow three times daily. If a previous run is still active, it is replaced by the new run.

## State and persistence behavior
The workflow persists fetched refs into the shared kernel repository PVC defined by overlays. The cron object itself stores only schedule/controller state.

## Dependencies and integration points
Depends on the workflow template, Argo controller installation, service accounts/RBAC, controller `/trees` endpoint, and the kernel disk PVC.

## Risks and edge cases
`Replace` can interrupt a long fetch and leave git locks or partial state; the template removes a stale `packed-refs.lock` at start as a mitigation. `startingDeadlineSeconds: 0` means missed schedules are not backfilled.

## Test signals
No direct test in this file. Cluster smoke tests include deployment of kernel-disk resources but do not necessarily wait for scheduled execution.
