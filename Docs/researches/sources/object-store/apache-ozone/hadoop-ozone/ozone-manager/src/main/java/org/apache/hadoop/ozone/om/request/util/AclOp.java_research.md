
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/util/AclOp.java

Purpose: Provides a concise functional-interface alias for ACL list update operations.

Important APIs and types: Extends `BiPredicate<List<OzoneAcl>, AclListBuilder>`.

Control flow: No methods beyond inherited `test`; implementers/lambdas decide whether and how an ACL operation changes the builder.

State and persistence behavior: No direct persistence. It operates on supplied ACL lists/builders in callers.

Dependencies and integration points: Used by ACL request helpers to avoid repeating long generic types for add/remove/set operations.

Risks and test signals: Behavioral tests belong to callers/lambdas. Compilation ensures type compatibility.
