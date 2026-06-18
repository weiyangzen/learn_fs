# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/AclListBuilder.java

Purpose: Copy-on-write builder for immutable `OzoneAcl` lists. It avoids allocating a new list when no ACL mutation happens.

Important APIs/types/functions: Static constructors `empty`, `of(ImmutableList)`, `of(List)`, and `copyOf` seed the builder. `add`, `addAll`, `set`, and `remove` delegate ACL merge/removal semantics to `OzoneAclUtil`. `build` returns the original immutable list unless `changed` is true.

Control flow and state: `updatedList` is lazily created from `originalList` on first mutation. `changed` is updated only when an actual ACL operation changes list content, except `set`, which compares the supplied list against the active list.

State and persistence behavior: No direct persistence. It is used by persistent metadata objects before they convert ACLs to protobuf.

Dependencies and integration points: Used by builders for keys, buckets, directories, and multipart key metadata. The List overload preserves binary compatibility across Guava versions.

Risks: `set` accepts a caller-provided list and documents that future mutations require it to be modifiable. Passing an immutable list and then calling `add` or `remove` can fail. Not thread-safe.

Test signals: Cover no-change build identity, add/merge semantics, removal, null handling, `set` with equal and different lists, and Guava compatibility path.
