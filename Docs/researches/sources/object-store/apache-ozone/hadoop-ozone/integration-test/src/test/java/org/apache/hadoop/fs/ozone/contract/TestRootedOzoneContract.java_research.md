# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/contract/TestRootedOzoneContract.java

## Purpose

`TestRootedOzoneContract` runs the common Ozone filesystem contract tests through the rooted OFS contract rather than the bucket-scoped Ozone contract. Its goal is to validate service-root path handling for Hadoop filesystem clients.

## Important APIs, Types, And Functions

The class extends `AbstractOzoneContractTest` and overrides `createContract(Configuration)` to return `new RootedOzoneContract(conf, getCluster())`.

## Control Flow

The inherited fixture starts or retrieves the MiniOzoneCluster, passes it to the rooted contract, and then executes the shared Hadoop FS contract tests with paths resolved from the OFS root URI.

## State And Persistence Behavior

No local state is added. Contract operations create and mutate Ozone volumes, buckets, and keys beneath the rooted namespace, and assertions validate that the root-level URI layer maps those operations correctly.

## Dependencies And Integration Points

The file depends on `AbstractFSContract`, Hadoop `Configuration`, `AbstractOzoneContractTest`, and `RootedOzoneContract`. It is the test-side integration point for `RootedOzoneContract`.

## Risks And Test Signals

Rooted OFS has broader namespace behavior than bucket-scoped `o3fs`; failures can reveal authority parsing, root listing, path qualification, or volume/bucket boundary issues. The test also depends on the shared abstract suite being broad enough to cover root-specific edge cases.
