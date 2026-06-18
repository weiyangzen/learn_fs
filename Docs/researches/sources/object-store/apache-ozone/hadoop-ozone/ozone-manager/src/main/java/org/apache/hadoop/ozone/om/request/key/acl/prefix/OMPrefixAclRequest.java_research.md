## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/key/acl/prefix/OMPrefixAclRequest.java

Purpose: `OMPrefixAclRequest` is the base class for add, remove, and set ACL operations on prefix resources. It handles linked-bucket prefix resolution, prefix validation, WRITE_ACL authorization, prefix locking, prefix table cache updates, response hooks, and audit setup.

Important APIs/types/functions: The central method is `validateAndUpdateCache`. Subclasses implement `getOzoneObj`, `onInit`, `onSuccess`, `onFailure`, `onComplete`, and `apply`. It uses `PrefixManagerImpl`, `OMPrefixAclOpResult`, `OmPrefixInfo`, `PREFIX_LOCK`, `OzoneFSUtils.isValidName`, `prefixManager.getResolvedPrefixObj`, `prefixManager.validateOzoneObj`, and the OM prefix table.

Control flow: The request resolves the incoming prefix object, validates the object and prefix path, checks WRITE_ACL on the resolved prefix if ACLs are enabled, and acquires the prefix write lock keyed by resolved prefix path. It reads existing prefix info, updates the update ID if present, calls the subclass operation through `PrefixManagerImpl`, and requires a non-null returned `OmPrefixInfo`. Remove requests that leave an empty ACL list tombstone the prefix row; other operations update the prefix row in cache.

State and persistence behavior: Prefix ACL state is represented in the prefix table and the in-memory prefix manager. Cache entries are written at the transaction index. Remove-to-empty deletes the prefix table entry, which avoids retaining empty prefix ACL rows. In HA, direct DB update exceptions from prefix manager operations are converted to a failed operation result rather than expected normal behavior.

Dependencies and integration points: It integrates OM prefix ACL APIs with linked-bucket resolution, native ACL authorization, prefix manager internals, prefix table persistence, OM lock details, metrics supplied to subclasses, and audit logging.

Risks and edge cases: Invalid prefix paths fail with `INVALID_PATH_IN_ACL_REQUEST`. If prefix resolution fails, audit falls back to the original object. Remove operations must correctly delete empty ACL rows. Correct lock keys depend on using the resolved prefix path, especially for linked buckets.

Test signals: Tests should cover prefix add/remove/set, linked bucket prefix resolution, invalid prefix names, remove-to-empty prefix deletion, missing prefix behavior, authorization failure, lock release, and prefix table replay.
