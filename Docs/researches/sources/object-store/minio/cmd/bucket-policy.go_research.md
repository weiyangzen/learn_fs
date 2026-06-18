# Research: sources/object-store/minio/cmd/bucket-policy.go

Purpose: provides the bucket policy subsystem and request-condition construction used by authorization decisions. It loads stored bucket policies, evaluates actions, maps request/credential/header/query context into policy condition keys, and converts between MinIO and minio-go policy representations.

Important APIs and functions: `PolicySys.Get` loads a bucket policy via `globalBucketMetadataSys.GetPolicyConfig`. `PolicySys.IsAllowed` evaluates `policy.BucketPolicyArgs`, falling back to owner-only allow when policy is absent. `getSTSConditionValues` extracts STS duration. `getConditionValues` builds policy condition values including time, source IP, user agent, referer, principal type, user IDs, version ID, signature version, auth type, location constraint, signature age, object tags, object-lock headers, arbitrary headers/query values, JWT string claims, and groups. `PolicyToBucketAccessPolicy` and `BucketAccessPolicyToPolicy` bridge MinIO's internal policy type with minio-go's type.

Control flow: condition construction normalizes derived credentials to parent user, classifies principal type, finds version ID from query or copy-source, maps auth type to signature/auth strings, clones headers and query values before consuming special keys, expands object tags into existing/request tag keys, appends duplicate values, and folds JWT/group claims into the result.

State and persistence behavior: the subsystem is read-only except for logging unexpected metadata errors. It consumes parsed policy objects stored by bucket metadata.

Dependencies and integration points: integrates auth credentials, request auth-type helpers, handler source IP utilities, MinIO HTTP constants, object tags parser, JWT claims, policy condition evaluation, and json/jsoniter conversion.

Risks: condition keys are string-sensitive and must match policy engine expectations. Header/query cloning prevents mutation of requests but broad inclusion of headers and query values means new request inputs can affect policy evaluation. Derived credential parent-user substitution is security-sensitive. `IsAllowed` logs unexpected errors and falls back to owner-only behavior, so metadata errors may deny non-owner access even if a policy should allow it.

Test signals: policy handler tests cover storing and fetching policies, and bucket handler tests indirectly cover anonymous policy authorization. There are no direct table tests in this subset for `getConditionValues`, JWT claims, object-lock condition keys, copy-source version IDs, or conversion helpers.
