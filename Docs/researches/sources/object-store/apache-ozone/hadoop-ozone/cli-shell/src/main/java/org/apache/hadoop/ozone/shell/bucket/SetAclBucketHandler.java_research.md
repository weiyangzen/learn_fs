## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/SetAclBucketHandler.java

Purpose: bucket-specific `setacl` shell command that replaces existing ACLs.

Important APIs and control flow: mixes in `BucketUri` and `AclOption`; `execute` calls `AclOption.setOn`, which invokes `ObjectStore.setAcl` with the parsed ACL list and prints success.

State and dependencies: persists replacement ACL set through OM. Depends on `AclHandler`, `AclOption`, and Ozone ACL object conversion.

Risks and test signals: replacement semantics are broader than add/remove and can remove existing ACLs not included by the user. No direct tests in this subset.
