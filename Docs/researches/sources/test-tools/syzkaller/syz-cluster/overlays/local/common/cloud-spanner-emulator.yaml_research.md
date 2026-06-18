# sources/test-tools/syzkaller/syz-cluster/overlays/local/common/cloud-spanner-emulator.yaml

## Purpose
Deploys a local Cloud Spanner emulator and service for local/test clusters.

## Important APIs, types, and functions
Creates `Deployment` `cloud-spanner-emulator` with one `gcr.io/cloud-spanner-emulator/emulator:latest` container exposing ports 9010 and 9020. Creates a `Service` exposing named `grpc` and `http` ports.

## Control flow
Local components use `SPANNER_EMULATOR_HOST: cloud-spanner-emulator:9010` from local config to connect to this service.

## State and persistence behavior
The emulator deployment has no persistent volume; database state is ephemeral across pod/cluster recreation.

## Dependencies and integration points
Used by local common overlay and database migration flow. Access is controlled by `network-policy-spanner.yaml`.

## Risks and edge cases
Image tag `latest` is floating. No resource limits or persistence are defined. Emulator behavior may differ from production Spanner.

## Test signals
Local cluster smoke migration and workload startup validate emulator reachability.
