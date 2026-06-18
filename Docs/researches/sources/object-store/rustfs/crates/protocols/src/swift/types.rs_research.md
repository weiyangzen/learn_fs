# sources/object-store/rustfs/crates/protocols/src/swift/types.rs

Defines shared Swift data structures used by listing and metadata flows.

Important API surface: `Container` serializes a container listing item with name, object count, total bytes, and optional last modified timestamp. `Object` serializes an object listing item with name, MD5/ETag hash, size, content type, and last modified timestamp. `SwiftMetadata` holds extracted custom metadata plus optional container read/write ACLs.

There is no behavior beyond serde serialization/deserialization and default construction for `SwiftMetadata`. These are in-memory DTOs: they mirror persisted Swift/S3 container/object metadata but do not perform reads or writes.

Dependencies are `serde` and `HashMap`. `Object` is used by static website directory listings, and container/object listing handlers can serialize these structures as Swift-compatible JSON responses.

Risks: timestamp fields are plain strings, so format consistency is enforced by producers rather than types. `SwiftMetadata` ACL fields are only containers for parsed values; authorization semantics must be implemented elsewhere. Dead-code allowances indicate some types are forward-facing API surface even when not locally referenced.

There are no tests in this file. Coverage is indirect through modules that construct or consume these DTOs, such as staticweb listing tests.
