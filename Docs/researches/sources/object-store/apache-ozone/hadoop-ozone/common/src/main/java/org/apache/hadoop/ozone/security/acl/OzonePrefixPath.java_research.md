# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/acl/OzonePrefixPath.java

Purpose: Interface for viewing an Ozone key prefix as a path tree during ACL checks, especially recursive prefix authorization.

Important APIs and types: `getOzoneFileStatus()` returns status for the represented path. `getChildren(String keyPrefix)` returns immediate child `OzoneFileStatus` entries for a directory-like prefix and may throw `IOException`.

Control flow: Interface only. Implementations should list only immediate children and avoid recursive traversal; the Javadoc gives examples for nested paths.

State and persistence behavior: No state in the interface. Implementations typically read OM key/table state to synthesize file statuses.

Dependencies and integration points: Referenced by `OzoneObj`/`OzoneObjInfo` and authorizers that need to recursively evaluate ACLs over prefix subpaths.

Risks: Recursive ACL behavior depends on implementations honoring immediate-child semantics. Returned iterators may represent live server-side state and throw during traversal depending on implementation.

Test signals: Implementation tests should cover file status retrieval, immediate child listing, directory versus file behavior, empty prefixes, and IOException propagation.
