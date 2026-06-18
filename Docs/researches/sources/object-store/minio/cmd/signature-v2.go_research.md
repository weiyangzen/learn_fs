# sources/object-store/minio/cmd/signature-v2.go

Purpose: This file implements AWS S3 Signature Version 2 validation and signing helpers for header-authenticated requests, presigned URLs, and browser POST policies. It canonicalizes x-amz headers and selected subresources, computes HMAC-SHA1 signatures, and maps malformed/authentication cases to MinIO S3 API errors.

Important APIs and types: `resourceList` is the sorted whitelist of query resources included in V2 canonical resources. `signV2Algorithm` is `"AWS"`. `doesPolicySignatureV2Match`, `doesPresignV2SignatureMatch`, `getReqAccessKeyV2`, `validateV2AuthHeader`, and `doesSignV2Match` are validation entry points. `calculateSignatureV2`, `preSignatureV2`, and `signatureV2` compute signatures. `compareSignatureV2` compares base64-decoded signatures in constant time. `canonicalizedAmzHeadersV2`, `canonicalizedResourceV2`, and `getStringToSignV2` build canonical signing inputs.

Control flow: Presigned validation splits `RequestURI`, unescapes query parameters, extracts access key/signature/expires, filters remaining queries, validates credentials, parses expiry, rejects expired URLs, resolves the canonical resource with virtual-host/domain support, computes the expected presign signature, compares it, and removes `Expires` from `r.Form`. Header validation checks the `Authorization` header prefix and access-key fields. Signed request validation parses raw URI/query, unescapes queries, resolves resource, ensures the auth prefix matches the credential access key, computes expected signature from method/resource/query/headers, and compares. Policy validation checks credential validity and compares the form policy signature.

State and persistence behavior: The code does not persist state. It reads request headers, URL/query data, global domain names, and credentials from IAM/auth validation. It mutates `r.Form` by deleting `Expires` after successful presign validation.

Dependencies and integration points: It integrates with MinIO's auth credential validation (`checkKeyValid`), S3 error codes, request resource parsing, domain-name support, and HTTP constants. It supports legacy V2 clients and is exercised by server tests when the suite signer is `signerV2`.

Risks: Signature V2 is legacy and sensitive to canonicalization details. `resourceList` must remain sorted and complete for supported subresources. Query unescaping and string joining must match client behavior for encoded values. `compareSignatureV2` rejects non-canonical base64 strings that cannot decode. Header canonicalization joins multiple values with commas but does not trim/fold whitespace beyond Go header normalization.

Test signals: `signature-v2_test.go` verifies resource-list sorting, presigned URL error cases and successful signatures, auth-header validation error mapping, and POST policy signature matching. `server_test.go` also runs the full S3 suite with signer V2 for ErasureSD.
