# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/contract/RootedOzoneContract.java

## Purpose

`RootedOzoneContract` is a Hadoop filesystem contract adapter for Ozone's rooted `ofs://` URI form. It specializes the shared `AbstractOzoneContract` test support so Hadoop FS contract tests can exercise a filesystem rooted at the Ozone service rather than at a single volume/bucket authority.

## Important APIs, Types, And Functions

The important type is `RootedOzoneContract`, a concrete subclass of `AbstractOzoneContract`. Its only local behavior is `getRootURI()`, which returns `OzoneConsts.OZONE_OFS_URI_SCHEME + "://" + OzoneConsts.OZONE_URI_DELIMITER`. The constructor accepts a Hadoop `Configuration` and `MiniOzoneCluster`, then delegates to the abstract superclass.

## Control Flow

Construction stores cluster/configuration behavior in the parent. During contract setup, the superclass asks for the root URI, and this class supplies `ofs:///`, allowing tests to resolve paths below the Ozone service root.

## State And Persistence Behavior

This class owns no mutable state beyond inherited test-cluster references. Persistence is entirely in the MiniOzoneCluster and Ozone Manager metadata touched by contract tests.

## Dependencies And Integration Points

It depends on Hadoop `Path`, `MiniOzoneCluster`, `OzoneConsts`, and the sibling `AbstractOzoneContract`. It integrates with `TestRootedOzoneContract`, which instantiates it from an Ozone configuration.

## Risks And Test Signals

The risk is URI-shape drift: rooted OFS behavior depends on the exact scheme and delimiter. Contract failures around path qualification, root listing, volume/bucket traversal, or authority parsing signal regressions.
