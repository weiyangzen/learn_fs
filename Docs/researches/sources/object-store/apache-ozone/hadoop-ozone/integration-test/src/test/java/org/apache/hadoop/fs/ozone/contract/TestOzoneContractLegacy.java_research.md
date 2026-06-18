# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/contract/TestOzoneContractLegacy.java

## Purpose

`TestOzoneContractLegacy` runs the same shared filesystem contract suite with the bucket layout forced to `LEGACY`. It protects compatibility for Ozone deployments and clients that still use the original key-layout semantics.

## Important APIs, Types, And Functions

The class extends `AbstractOzoneContractTest`. Its `createOzoneConfig()` override sets `OZONE_DEFAULT_BUCKET_LAYOUT` to `LEGACY.name()`. Its `createContract(Configuration)` override returns an `OzoneContract`, which supplies the `o3fs` contract implementation.

## Control Flow

The inherited test harness requests the configuration, receives the legacy layout override, creates the Ozone FS contract, and executes the inherited Hadoop contract tests against a MiniOzoneCluster-backed filesystem.

## State And Persistence Behavior

The only local state is configuration. Persistent behavior lives in the OM bucket layout and key metadata created during the test run. Legacy buckets store path-like keys without the FSO directory table behavior, so this file validates the older persistence shape.

## Dependencies And Integration Points

Dependencies include `OMConfigKeys`, `BucketLayout.LEGACY`, `OzoneConfiguration`, and `OzoneContract`. It complements `TestOzoneContractFSO` by keeping both metadata layouts under the same contract expectations.

## Risks And Test Signals

The main risk is accidental preference for FSO semantics in shared filesystem code. Contract failures in directory markers, parent handling, rename/delete, or path qualification under the legacy configuration indicate compatibility regressions.
