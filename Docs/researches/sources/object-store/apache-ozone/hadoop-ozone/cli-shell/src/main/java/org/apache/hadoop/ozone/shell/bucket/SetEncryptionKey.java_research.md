## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/SetEncryptionKey.java

Purpose: hidden deprecated bucket command to reset a bucket encryption key for buckets affected by historical HDDS-7449/HDDS-7526 issues.

Important APIs and control flow: command `set-encryption-key` is hidden and deprecated. It accepts `--key`/`-k`, resolves the target bucket through the object store, and calls `bucket.setEncryptionKey(bekName)`.

State and dependencies: persists bucket encryption metadata through OM RPC. Depends on `BucketHandler` and `OzoneBucket`.

Risks and test signals: the Javadoc explicitly warns this does not alter existing keys and later writes only are affected. The command is hidden because resetting encryption after creation is not normal user flow. No direct tests in this subset.
