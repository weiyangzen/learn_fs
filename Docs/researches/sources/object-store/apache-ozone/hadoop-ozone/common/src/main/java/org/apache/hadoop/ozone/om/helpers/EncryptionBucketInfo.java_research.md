# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/EncryptionBucketInfo.java

Purpose: Public evolving descriptor for an encrypted bucket/encryption zone: path, ID, cipher suite, crypto protocol version, and key name.

Important APIs/types/functions: Constructor sets all fields. Accessors expose ID/path/crypto metadata. `equals`, `hashCode`, and `toString` cover all fields.

Control flow and state: Immutable value object with no branching other than equality.

State and persistence behavior: Represents listed encryption bucket state; persistence is external. The ID supports batched listing.

Dependencies and integration points: Integrates with Hadoop crypto types and Ozone encryption bucket listing APIs.

Risks: Constructor does not validate path, key name, or crypto fields. The class is public/evolving, so serialization expectations may exist outside this module.

Test signals: Equality/hash behavior, listing order around ID boundaries, and null field expectations if callers rely on permissive construction.
