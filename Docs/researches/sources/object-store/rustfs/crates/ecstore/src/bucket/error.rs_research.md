# sources/object-store/rustfs/crates/ecstore/src/bucket/error.rs

Purpose: bucket metadata error enum for missing bucket-level configuration documents and IO/other failure normalization.

Important APIs and types: `BucketMetadataError` variants represent missing tagging, policy, object lock, lifecycle, SSE, quota, replication, and remote target configs, plus `Io(std::io::Error)`. `other` wraps arbitrary errors into `std::io::Error::other`. `to_u32` and `from_u32` provide numeric mapping for serialization or cross-boundary error codes.

Control flow: `From<crate::error::Error>` maps underlying IO directly and wraps all other crate errors. `From<std::io::Error>` attempts to downcast back to `BucketMetadataError`, otherwise wraps as `Io`. `PartialEq` compares IO by kind/message and non-IO by numeric code.

State and persistence: no state. Numeric codes are persistent contract material if stored or sent over RPC.

Dependencies and integration points: depends on crate-level `Error`, `thiserror`, and std IO error handling. Used by bucket metadata systems to distinguish absent optional configs from hard failures.

Risks: `from_u32(0x09)` reconstructs a generic IO error, losing original details. Numeric code stability matters for compatibility. Equality on IO message can be brittle.

Test signals: no direct tests in this file; coverage should come from metadata load/save and RPC/error-code tests.
