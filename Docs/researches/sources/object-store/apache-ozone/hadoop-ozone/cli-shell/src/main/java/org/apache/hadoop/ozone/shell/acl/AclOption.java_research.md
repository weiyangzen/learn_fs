## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/acl/AclOption.java

Purpose: reusable ACL list option and operation helper for add/remove/set ACL commands.

Important APIs and control flow: an exclusive arg group accepts modern `--acls`/`--acl`/`-a` or hidden deprecated `-al`, split by comma, with conversion through `OzoneAcl.parseAcl`. `addTo`, `removeFrom`, and `setOn` call the corresponding `ObjectStore` ACL method and print per-ACL result messages or a set success line.

State and dependencies: parse-time ACL array state only; actual ACL persistence is handled by OM through `ObjectStore`. Depends on Guava immutable lists, `OzoneAcl`, and `ObjectStore`.

Risks and test signals: repeated add/remove operations are not transactional across multiple ACLs, so partial success is possible. Deprecated option remains accepted for compatibility.
