# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/key/acl/prefix/package-info.java

Purpose: This package documentation marks the package as containing prefix ACL response classes.

Important APIs and types: The package centers on `OMPrefixAclResponse`, which persists `OmPrefixInfo` to `PREFIX_TABLE`.

Control flow: Prefix ACL request handlers compute the resulting prefix ACL state; the response writes or deletes the prefix table row during DB batch application.

State and persistence behavior: State changes are limited to prefix ACL metadata. Removing the last ACL deletes the prefix entry.

Dependencies and integration points: The package integrates prefix ACL requests, OM metadata prefix table, cleanup annotations, and standard response success gating.

Risks and test signals: Tests should cover add, set, remove-one, and remove-last behaviors, including failed response no-op.
