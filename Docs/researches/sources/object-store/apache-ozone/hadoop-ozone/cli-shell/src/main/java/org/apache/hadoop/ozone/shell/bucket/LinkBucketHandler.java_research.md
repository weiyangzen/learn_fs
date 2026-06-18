## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/LinkBucketHandler.java

Purpose: bucket `link` command that creates a bucket link pointing to another bucket.

Important APIs and control flow: takes two positional `BucketUri` parameters: source and target. `getAddress` returns source so client resolution follows the source URI. `execute` builds `BucketArgs` with source volume and bucket, resolves the target volume, creates the target bucket as a link, and prints it in verbose mode.

State and dependencies: persists link bucket metadata through OM RPC. Depends on `BucketArgs`, `StorageType.DEFAULT`, `OzoneVolume`, and bucket URI validation.

Risks and test signals: client connection is based on source address, so cross-cluster source/target semantics are not supported here. No direct tests in this subset.
