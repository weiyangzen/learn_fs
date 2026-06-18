# sources/object-store/rustfs/crates/iam/src/error.rs

`error.rs` defines the IAM crate's `Error` enum and `Result<T>` alias. Variants cover policy, string, crypto, missing user/account/service/temp/group/policy, policy-in-use, group-not-empty, invalid arguments/service/action/token/access keys/secret keys/expiration, credential state, policy size, config not found, IO, and already initialized errors.

The file implements `PartialEq`, `Clone`, `Error::other`, conversions to/from `rustfs_ecstore::StorageError`, conversion from `rustfs_policy::error::Error`, and conversions from IAM error to IO plus serde/base64 errors into IAM. Helper predicates identify config-not-found and missing policy/user/account/temp/group/service-account cases.

There is no runtime state. This file is the conversion boundary for IAM store, manager, sys, and OIDC code. Risks include clone changing complex variants into `StringError` and IAM-to-IO conversion using `ErrorKind::Other`, which loses original IO kind for downstream code. Tests cover storage/policy/JSON/IO conversions, helper predicates, display strings, and `Error::other`.
