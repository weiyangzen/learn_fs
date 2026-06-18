# sources/object-store/minio-mc/cmd/share-upload_test.go

## Purpose
Tests shell escaping in upload share curl command generation.

## Important APIs, types, and functions
- `TestMakeCurlCmdEscapesSpecialChars` drives `makeCurlCmd` with keys containing shell-special characters and checks the generated command contains escaped `key=` form fields.

## Control flow
The test table enumerates object keys and expected escaped values. For each case it calls `makeCurlCmd(key, "http://example.com", false, map[string]string{})` and asserts the resulting command string contains ` key=<escaped> `.

## State and persistence
No state. It does not touch share DB files or remote clients.

## Dependencies and integration points
Depends on `makeCurlCmd` and indirectly `shellQuote`. Uses Go `testing` and `strings.Contains`.

## Risks and edge cases
- The test only checks non-recursive command generation with an empty `uploadInfo` map.
- It does not assert POST URL quoting, form field ordering, recursive `<NAME>` behavior, or upload metadata fields.

## Test signals
This is a direct regression signal for command injection/shell escaping risks in generated curl commands.
