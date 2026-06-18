# sources/object-store/minio/cmd/postpolicyform.go

## Purpose
This file parses and validates S3 POST policy forms. It converts JSON policy documents into strict internal structures and checks request form fields against the declared policy conditions.

## Important APIs, Types, and Functions
`startsWithConds` defines which keys permit `starts-with`. `contentLengthRange` and `PostPolicyForm` model parsed policy state. `sanitizePolicy` uses `jstream` to reject duplicate top-level JSON keys before standard decoding. `parsePostPolicyForm` decodes expiration and conditions, accepting map conditions and array conditions for `eq`, `starts-with`, and `content-length-range`. `checkPostPolicy` enforces expiration, condition matching, multiple-value rejection, and the rule that every non-exempt form field appears in policy conditions.

## Control Flow and State
Parsing first sanitizes, then decodes with `DisallowUnknownFields`. Validation builds a `mustFindInPolicy` map from canonicalized form fields, removes exemptions, evaluates each policy condition, and fails if unaccounted fields remain.

## Dependencies and Integration Points
The file integrates with POST policy handlers, MinIO HTTP constants, encryption header exceptions, minio-go set helpers, and S3-select `jstream`.

## Risks and Test Signals
Policy parsing is security-sensitive. Duplicate key rejection prevents malicious JSON overriding, and strict field coverage blocks hidden form inputs. Content-length range is parsed here but enforced by the handler. `postpolicyform_test.go` and `post-policy_test.go` cover duplicate rejection, expiration, condition failures, exceptions, and checksum/header omissions.
