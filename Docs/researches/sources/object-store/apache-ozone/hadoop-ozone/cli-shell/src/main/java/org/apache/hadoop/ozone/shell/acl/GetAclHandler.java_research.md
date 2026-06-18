## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/acl/GetAclHandler.java

Purpose: abstract implementation for ACL read commands with JSON or compact string output.

Important APIs and control flow: option `--json` is negatable and defaults true. `execute` fetches ACLs through `client.getObjectStore().getAcl(obj)`, prints pretty JSON by default, or joins ACL strings with commas. `formatAcl` strips trailing `[ACCESS]` to make non-JSON output compatible with set/add input syntax while preserving non-default scopes.

State and dependencies: read-only client operation; no persistence in this class. Depends on `AclHandler`, `OzoneAcl`, and JSON helper inherited from `Handler`.

Risks and test signals: string formatting uses regex replacement on `OzoneAcl.toString`, so changes to ACL string format could affect compatibility. Bucket-specific `GetAclBucketHandler` extends it.
