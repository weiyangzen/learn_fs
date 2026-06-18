# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/acl/OzoneObjInfo.java

Purpose: Concrete immutable Ozone ACL object for volume, bucket, key, and prefix resources.

Important APIs and types: Stores volume name, bucket name, and a shared `name` field for key or prefix. Methods implement full path construction, protobuf parsing, getters, builder helpers, and equality/hash. Builder supports `fromKeyArgs`, `fromOzoneObj`, and field setters.

Control flow: `getPath` builds slash-delimited paths based on resource type. `fromProtobuf` splits the protobuf path into at most three tokens and validates the number of components required for each resource type before building an object. Builder does not validate required fields at build time beyond `OzoneObj` type null checks.

State and persistence behavior: In-memory object identity used for ACL checks and ACL RPC payloads. Protobuf path strings are the serialized boundary.

Dependencies and integration points: Used by client ACL APIs, OM ACL metadata, authorizers, `OmKeyArgs`, and `OzonePrefixPath` viewers for recursive prefix checks.

Risks: Path parsing depends on delimiter normalization and paths with missing components throw `IllegalArgumentException`. Builder allows inconsistent states such as key resource with null name. Key and prefix share the same `name` slot, so callers must set the correct setter for clarity.

Test signals: Path generation for each resource type, protobuf round-trip, malformed path rejection, builder helpers from key args/object, equality including prefix path viewer, and null-field behavior.
