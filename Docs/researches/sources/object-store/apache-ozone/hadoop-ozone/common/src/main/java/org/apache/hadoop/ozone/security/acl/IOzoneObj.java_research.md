# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/acl/IOzoneObj.java

Purpose: Marker interface for objects that can participate in Ozone authorization.

Important APIs and types: Empty interface implemented by `OzoneObj`.

Control flow: No logic.

State and persistence behavior: None.

Dependencies and integration points: Used by `IAccessAuthorizer.checkAccess` and AssumeRole grants to accept Ozone object abstractions without depending on a concrete implementation.

Risks: Marker-only design means authorizers often need casts or reflective knowledge of supported implementations.

Test signals: No direct tests beyond authorizer compatibility with concrete `OzoneObj` implementations.
