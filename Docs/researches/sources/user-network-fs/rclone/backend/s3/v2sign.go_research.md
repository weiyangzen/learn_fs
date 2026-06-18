# sources/user-network-fs/rclone/backend/s3/v2sign.go

## Purpose
This file implements legacy S3 Signature Version 2 signing behind the AWS SDK v2 `HTTPSignerV4` interface. It supports older S3-compatible services that do not accept v4 signatures, such as older Ceph deployments.

## Important APIs, Types, And Functions
`s3ParamsToSign` lists subresource and response override query parameters that must be included in the S3 v2 canonical resource. `v2Signer` stores a pointer to backend `Options`. Its `SignHTTP` method sets the `Date` header, canonicalizes the escaped path, extracts Content-MD5 and Content-Type, collects and sorts `x-amz-*` headers, includes selected query parameters, computes an HMAC-SHA1 over the v2 string-to-sign using `SecretAccessKey`, base64-encodes the result, and sets the `Authorization: AWS accessKey:signature` header.

## Control Flow
`s3Connection` installs `v2Signer` when `--s3-v2-auth` is enabled or the region is `other-v2-signature`, except for IBM COS IAM where a separate signer is used. The SDK invokes `SignHTTP` during request finalization, even though the implementation ignores v4-specific inputs such as `payloadHash`, `service`, `region`, and signer option callbacks.

## State And Persistence Behavior
The signer mutates outgoing HTTP requests by setting `Date` and `Authorization`. It reads credentials from `Options` and does not maintain its own cache or persistent state.

## Dependencies And Integration Points
The implementation depends on standard HMAC/SHA1/base64/http utilities and AWS SDK v2 signer interface types. It integrates with the S3 backend's request middleware and option handling. It is intentionally compatible-shaped with v4 signing even though it produces v2 signatures.

## Risks And Edge Cases
Signature v2 is legacy and less broadly supported. Canonicalization correctness is sensitive to path escaping, query parameter inclusion, repeated query values, and `x-amz-*` header ordering/value joining. The code uses `time.Now()` instead of the `signingTime` parameter, which is acceptable for normal use but makes deterministic signing tests harder. It references `v2.opt.SecretAccessKey` and `AccessKeyID` directly rather than the `credentials` argument, so assume-role or environment credential flows should not be expected to work through this signer unless options contain the final static credentials.

## Test Signals
There are no direct unit tests in this subset for v2 signatures. Coverage is likely through live provider integration when `v2_auth` is configured. High-value tests would check known AWS v2 signing examples, repeated subresource query parameters, and canonical `x-amz-*` headers.
