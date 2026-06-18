# sources/object-store/minio/cmd/postpolicyform_test.go

## Purpose
This file unit-tests POST policy parsing and condition checking independent of the HTTP handler.

## Important APIs, Types, and Functions
`TestParsePostPolicyForm` checks missing expiration, invalid JSON, duplicate `expiration`, duplicate `conditions`, duplicate bucket-condition payloads through repeated top-level keys, and a valid policy. `formValues` is a small fluent wrapper around `http.Header`. `TestPostPolicyForm` builds a minio-go post policy and validates many form-field permutations against `checkPostPolicy`.

## Control Flow and State
Tests generate current or expired policy documents, base64 encode/decode as the handler would, parse with `parsePostPolicyForm`, and compare exact error strings from `checkPostPolicy`.

## Dependencies and Integration Points
The tests depend on minio-go post policy generation, MinIO HTTP header constants, and the parser/validator in `postpolicyform.go`.

## Risks and Test Signals
The tests are high-value security regression signals for duplicate JSON handling, unsupported hidden fields, multiple form values, V2 signature exceptions, x-ignore fields, and SSE header exceptions. Exact error string assertions can be brittle if messages are refactored.
