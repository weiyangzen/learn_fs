# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestAclListBuilder.java

Purpose: tests `AclListBuilder`, a mutation-tracking helper for ACL lists that preserves immutable inputs when no effective change occurs.

Important APIs/types/functions: exercises `AclListBuilder.of`, `copyOf`, `add`, `addAll`, `set`, `remove`, `build`, and `isChanged`.

Control flow and state: test data includes `alice` read/write ACLs that merge into one read-write entry and a separate `bob` read ACL. Reapplying the same operation returns false while preserving an already-true changed flag. `set` with same or equal list leaves the builder unchanged and returns the original list instance.

Dependencies and integration points: depends on `OzoneAcl.of` and ACL identity/type/scope enums. Builder behavior is important for OM metadata update paths that should avoid writing unchanged ACL lists.

Risks and test signals: catches duplicate ACL entries, lost merged rights, false positive dirty state, and no-op operations resetting dirty state. The instance identity assertions protect memory and persistence churn optimizations.
