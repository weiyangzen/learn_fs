<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/access-perms.go -->
# sources/object-store/minio-mc/cmd/access-perms.go

## Purpose
Defines accepted bucket access-permission labels and validation for custom policy JSON files used by MinIO client policy/access commands.

## Important APIs, types, and functions
`accessPerms` is a string type with constants `none`, `download`, `upload`, `private`, `public`, and `custom`. Methods `isValidAccessPERM` and `isValidAccessFile` validate built-in labels or parse a policy file.

## Control flow
Built-in validation switches over known constants. File validation opens the named path, decodes JSON into `policy.BucketAccessPolicy`, enforces version `2012-10-17`, and ensures each statement effect is `Allow` or `Deny`.

## State and persistence behavior
Reads a local policy file but writes no state. Fatal messages are emitted through the shared CLI error path for invalid files.

## Dependencies and integration points
Depends on MinIO color JSON decoder and `minio-go` policy types. Integrated by commands that accept canned or custom bucket policies.

## Risks and test signals
The method returns false after `fatalIf`, so callers must not assume nonfatal validation. Tests should cover missing files, malformed JSON, bad version/effect, and every supported canned permission.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/access-perms.go -->
