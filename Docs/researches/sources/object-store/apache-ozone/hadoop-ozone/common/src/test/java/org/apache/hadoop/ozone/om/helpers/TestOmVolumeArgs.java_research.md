# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmVolumeArgs.java

Purpose: tests `OmVolumeArgs` builder ACL mutation behavior and copy semantics.

Important APIs/types/functions: exercises `OmVolumeArgs.Builder`, `copyObject`, `toBuilder`, `addAcl`, `setAcls`, `removeAcl`, metadata addition, quota/object/update IDs, and ACL getters.

Control flow and state: setup obtains the current user. `createSubject` builds a volume with owner, admin, metadata, quota, object/update IDs, and a read ACL. Tests assert `copyObject` returns the same instance, adding write rights changes the ACL entry, setting ACLs replaces the list, and removing the read ACL yields an empty list.

Dependencies and integration points: uses `UserGroupInformation`, `OzoneAcl`, Guava `ImmutableMap`, and `Time`. These args back OM volume table records and ACL updates.

Risks and test signals: highlights that `copyObject` is identity-returning, so callers must not assume deep copy. ACL builder operations are the main regression surface covered here.
