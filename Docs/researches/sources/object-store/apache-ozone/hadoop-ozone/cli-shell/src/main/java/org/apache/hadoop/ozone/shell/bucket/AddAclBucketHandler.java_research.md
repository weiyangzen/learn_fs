## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/AddAclBucketHandler.java

Purpose: bucket-specific `addacl` shell command.

Important APIs and control flow: mixes in `BucketUri` for validated `volume/bucket` address and `AclOption` for one or more ACLs. `getAddress` returns the bucket address, and `execute` delegates to `AclOption.addTo` with the client object store and output writer.

State and dependencies: ACL changes persist through OM via `ObjectStore.addAcl`; this handler holds only parsed CLI state. Depends on `AclHandler`, `BucketUri`, and `AclOption`.

Risks and test signals: multiple ACLs can partially succeed because each is added independently. No direct tests in this subset.
