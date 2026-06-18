# sources/object-store/rustfs/crates/ecstore/src/bucket/policy_sys.rs

Purpose: Thin policy authorization facade over bucket metadata. It retrieves a bucket policy and evaluates request arguments, falling back to owner-only access when no policy exists.

Important APIs and types: `PolicySys::is_allowed` accepts `BucketPolicyArgs` and calls `BucketPolicy::is_allowed`. `PolicySys::get` reads `BucketMetadataSys` and returns the parsed `BucketPolicy`.

Control flow and state: `is_allowed` attempts to load the policy for `args.bucket`. If it succeeds, policy evaluation decides. If config is not found, or another error occurs after logging, the result falls back to `args.is_owner`. No state is mutated in this file.

Dependencies and integration: Depends on the global metadata system and `rustfs_policy` types. It is likely called by S3 API authorization paths needing bucket policy checks.

Risks: Non-ConfigNotFound errors are logged but still result in owner fallback; that is safe for non-owners but may mask availability/config problems for owners. It does not expose raw policy JSON; raw retrieval is in `metadata_sys`.

Test signals: No direct tests. Policy correctness depends on `rustfs_policy` tests and metadata system behavior.
