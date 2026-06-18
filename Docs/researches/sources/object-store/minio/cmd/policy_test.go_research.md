# sources/object-store/minio/cmd/policy_test.go

## Purpose
This file tests bucket policy permission evaluation and conversion between MinIO's internal bucket policy type and minio-go bucket access policy structures.

## Important APIs, Types, and Functions
`TestPolicySysIsAllowed` builds a policy with get-location and put-object allows, then verifies anonymous and owner actions across matching and nonmatching buckets. `getReadOnlyStatement` creates minio-go read-only statements. `TestPolicyToBucketAccessPolicy` and `TestBucketAccessPolicyToPolicy` check round-trip conversion and invalid version errors.

## Control Flow and State
Tests are table-driven and compare exact booleans, errors, and deep-equal policy structures. There is no persistent state.

## Dependencies and Integration Points
The tests depend on `github.com/minio/pkg/v3/policy`, policy conditions, minio-go policy types, and conversion functions implemented elsewhere in the cmd package.

## Risks and Test Signals
The tests guard policy compatibility and owner bypass behavior for bucket-level access. They do not cover deny statements, condition-rich policies, wildcard principals beyond `*`, or JSON serialization, so broader policy tests are needed elsewhere.
