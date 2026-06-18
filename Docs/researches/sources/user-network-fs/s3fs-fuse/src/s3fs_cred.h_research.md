# sources/user-network-fs/s3fs-fuse/src/s3fs_cred.h

Purpose: declares the `S3fsCred` singleton and credential-management contract for the rest of s3fs-fuse. It centralizes credential source configuration, mutable access-token state, IAM metadata settings, external credential library function pointers, and public auth entry points.

Important APIs and types: `iamcredmap_t` maps IAM response fields. `S3fsCred::get()` provides the process-wide singleton. Public APIs include `SetBucket`, `GetBucket`, `IsIBMIAMAuth`, `LoadIAMRoleFromMetaData`, `CheckIAMCredentialUpdate`, `GetCredFuncVersion`, `DetectParam`, and `CheckAllParams`. Private APIs model local credential files, AWS profiles, IAM/ECS/IBM URLs and parsing, token refresh, external library loading, and bucket-parameter validation. Constants define IAM metadata endpoints, IMDSv2 headers, token TTL, field names, and refresh margin.

Control flow: callers configure the singleton through option detection, then call `CheckAllParams` during mount setup. After setup, request signing code calls `CheckIAMCredentialUpdate` to get current credential material and trigger refresh as needed. IAM role auto-detection is separated into `LoadIAMRoleFromMetaData`, allowing curl initialization before metadata access.

State and persistence: the class owns process memory for secrets, tokens, expiration, IAM role, selected profile, passwd-file path, plugin path/options, and plugin handles. Thread-safety annotations mark credential/token fields as guarded by `token_lock`, but some flags and configuration strings are not annotated and are expected to be startup-only.

Dependencies and integration points: includes `s3fs_extcred.h` for plugin ABI typedefs, `types.h`/`common.h` for shared maps and annotations, and is used by curl/auth, option parsing, and mount initialization code.

Risks: the header exposes only coarse public operations, which is good for containment, but the singleton means tests and repeated mounts must carefully reset process state. Returning `const std::string&` from locked accessors can be unsafe if references escape the lock; public `GetIAMRole()` currently returns a reference after releasing its local lock. Plugin ABI function pointers require exact C symbol signatures.

Test signals: compile-time thread-safety annotation checks, singleton lifecycle tests, option-detection table tests, and tests that call public APIs in the same order as mount startup and request signing.
