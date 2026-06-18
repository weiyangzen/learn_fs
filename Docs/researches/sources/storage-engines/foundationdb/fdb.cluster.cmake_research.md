# sources/storage-engines/foundationdb/fdb.cluster.cmake

## Purpose
CMake template for a local FoundationDB cluster file using a loopback coordinator.

## Important APIs, Types, and Functions
Contains the cluster connection string template `${CLUSTER_DESCRIPTION1}:${CLUSTER_DESCRIPTION1}@127.0.0.1:4000`, corresponding to `description:id@coordinator`.

## Control Flow
No executable flow. CMake substitutes `CLUSTER_DESCRIPTION1` during configuration.

## State and Persistence Behavior
The rendered file is persistent client configuration. It controls which cluster local tools and tutorials open.

## Dependencies and Integration Points
Depends on CMake variable substitution and FoundationDB cluster-file parsing. Integrates with local development clusters and tutorial defaults such as `fdb.cluster`.

## Risks
Only appropriate for local development. If copied elsewhere, clients will try loopback and likely the wrong cluster id.

## Test Signals
Verify generated output has no `${...}` placeholders and can open a matching local cluster at `127.0.0.1:4000`.
