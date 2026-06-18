# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOmStartupSlvLessThanMlv.java

## Purpose
Verifies OM refuses to start when the on-disk metadata layout version is newer than the software layout version supported by the running binary.

## Important APIs, types, and functions
- Uses `OMLayoutFeature.values()` to compute the largest supported software layout version.
- Uses `UpgradeTestUtils.createVersionFile` with `HddsProtos.NodeType.OM` to create a VERSION file.
- Starts through `MiniOzoneCluster.newBuilder(conf).build()` and expects `OMException`.

## Control flow
The test creates an `om/current` directory inside a JUnit temp folder, points `OZONE_OM_DB_DIRS` at that folder, writes a VERSION file with MLV set to `largestSlv + 1`, then builds a MiniOzoneCluster under disabled logging. Startup must throw before the cluster is usable.

## State and persistence behavior
The only persisted state is the VERSION file under OM metadata storage. The version manager must compare the stored metadata layout version against compiled layout features and reject future metadata to avoid unsafe downgrade/open behavior.

## Dependencies and integration points
This test integrates upgrade layout metadata, OM storage initialization, MiniOzoneCluster startup, and `MiniOzoneClusterImpl` logging. It is a guard for upgrade/downgrade compatibility logic.

## Risks and edge cases
The assertion hard-codes the exact exception message using `mlv` and `mlv - 1`, so message changes or non-contiguous layout versions can affect it. It does not test equal versions, lower versions, or HA storage directories.

## Test signals
Expected signal is an `OMException` from cluster build with the precise message that metadata layout version is greater than software layout version.
