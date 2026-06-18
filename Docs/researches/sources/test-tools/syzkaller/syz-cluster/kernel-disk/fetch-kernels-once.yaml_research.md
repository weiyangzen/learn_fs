# sources/test-tools/syzkaller/syz-cluster/kernel-disk/fetch-kernels-once.yaml

## Purpose
Defines a manually triggerable one-shot Argo workflow for fetching kernel repositories.

## Important APIs, types, and functions
Creates an Argo `Workflow` with generated name prefix `fetch-kernels-manual-` and `workflowTemplateRef` pointing to `fetch-kernels-workflow-template`.

## Control flow
When submitted, Argo instantiates the shared fetch-kernels template once.

## State and persistence behavior
Uses the same persistent kernel repository PVC through the template. The workflow object records only run state.

## Dependencies and integration points
Requires the workflow template and Argo installation. Useful for manual refresh or debugging outside the cron cadence.

## Risks and edge cases
Manual runs can overlap scheduled runs unless operators coordinate. Overlap on the same bare repository PVC can cause git locking/contention.

## Test signals
No direct automated test; operational utility manifest.
