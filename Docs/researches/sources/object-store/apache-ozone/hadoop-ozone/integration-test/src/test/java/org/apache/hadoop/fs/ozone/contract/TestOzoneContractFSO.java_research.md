# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/contract/TestOzoneContractFSO.java

## Purpose

`TestOzoneContractFSO` runs the shared Ozone filesystem contract suite against buckets created with the `FILE_SYSTEM_OPTIMIZED` layout. It verifies that the Hadoop `o3fs` contract still holds when Ozone uses directory-aware FSO metadata internally.

## Important APIs, Types, And Functions

The class extends `AbstractOzoneContractTest`. It overrides `createOzoneConfig()` to call the superclass, then sets `OZONE_DEFAULT_BUCKET_LAYOUT` to `FILE_SYSTEM_OPTIMIZED.name()`. It overrides `createContract(Configuration)` and returns a new `OzoneContract`.

## Control Flow

The abstract test harness creates an `OzoneConfiguration`, applies the FSO bucket-layout override, starts or accesses the MiniOzoneCluster, and runs inherited Hadoop FS contract tests through the returned `OzoneContract`.

## State And Persistence Behavior

The file itself is stateless. The meaningful state is bucket layout selection in configuration and the OM metadata entries created by contract operations. FSO layout persists directory and file entries differently from legacy buckets, so the contract validates both path semantics and metadata backend compatibility.

## Dependencies And Integration Points

It depends on `OMConfigKeys.OZONE_DEFAULT_BUCKET_LAYOUT`, `BucketLayout.FILE_SYSTEM_OPTIMIZED`, `OzoneConfiguration`, and `OzoneContract`. It is paired with the legacy and rooted contract tests to cover layout variants.

## Risks And Test Signals

Risks include contract gaps masked by shared setup and behavior differences between FSO directories and Hadoop path expectations. Failures in rename, delete, mkdirs, list status, or file creation under this class are strong signals of FSO-specific filesystem regressions.
