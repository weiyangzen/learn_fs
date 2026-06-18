# sources/storage-engines/foundationdb/fdbkubernetesmonitor/api/.testdata/test_env.sh

## Purpose
This shell fixture exports local environment variables for Kubernetes monitor API/manual tests.

## Important APIs, Types, And Functions
It sets `FDB_PUBLIC_IP`, `FDB_POD_IP`, `FDB_ZONE_ID`, `FDB_MACHINE_ID`, `FDB_INSTANCE_ID`, `KUBERNETES_SERVICE_HOST`, and `KUBERNETES_SERVICE_PORT`.

## Control Flow
There is no branching. Sourcing the file populates the shell environment for configs that use environment-backed arguments.

## State And Persistence Behavior
It mutates only the current shell environment and persists no files.

## Dependencies And Integration Points
It pairs with `.testdata/default_config.json` and any monitor code that reads Kubernetes/FDB environment variables.

## Risks And Edge Cases
Values are localhost/docker-desktop oriented and not representative of real pod networking. Tests that rely on the host system environment may behave differently from tests that pass an explicit env map.

## Test Signals
A simple signal is that sourcing this file allows default configuration argument generation without missing-environment errors.
