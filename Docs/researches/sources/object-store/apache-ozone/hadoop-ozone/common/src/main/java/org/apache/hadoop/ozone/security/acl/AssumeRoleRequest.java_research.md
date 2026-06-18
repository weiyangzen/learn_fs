# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/acl/AssumeRoleRequest.java

Purpose: Immutable data carrier for authorizing an S3 STS AssumeRole request through `IAccessAuthorizer`.

Important APIs and types: Fields include host, IP, client UGI, target role name, and optional grants. Nested immutable `OzoneGrant` encapsulates object set, ACL permission set, and optional S3 action restrictions.

Control flow: Constructors assign fields; getters expose them; equality/hash cover all fields. `OzoneGrant` with S3 actions defensively wraps a `LinkedHashSet` in an unmodifiable set. The two-argument grant constructor uses an empty action set to mean no S3 action restriction.

State and persistence behavior: Immutable request object with in-memory authorization inputs. It does not persist grants or session policies itself.

Dependencies and integration points: Passed to `IAccessAuthorizer.generateAssumeRoleSessionPolicy`; ties together `UserGroupInformation`, `IOzoneObj`, ACL types, and S3 action names parsed from session policies.

Risks: The outer `grants` set is not defensively copied, so immutability depends on caller discipline. `null` grants means no extra limitation beyond role, while an empty set means no access; tests and callers must preserve this distinction.

Test signals: Cover equality/hash, S3 action immutability, null versus empty grant semantics in authorizers, and mutation behavior for caller-provided grant sets.
