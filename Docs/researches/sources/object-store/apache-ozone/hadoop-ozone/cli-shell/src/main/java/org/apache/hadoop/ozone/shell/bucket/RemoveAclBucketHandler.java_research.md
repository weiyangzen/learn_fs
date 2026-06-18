## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/RemoveAclBucketHandler.java

Purpose: bucket-specific `removeacl` shell command.

Important APIs and control flow: mixes in validated `BucketUri` and `AclOption`. `execute` delegates to `AclOption.removeFrom`, which iterates parsed ACLs and calls `ObjectStore.removeAcl`.

State and dependencies: persists ACL removals through OM RPCs. Depends on `AclHandler`, `AclOption`, and bucket address conversion.

Risks and test signals: multi-ACL removal is not transactional and prints per-ACL existence/success messages. No direct tests in this subset.
