# sources/object-store/minio-mc/cmd/share-upload-main.go

## Purpose
Implements `mc share upload`, generating a presigned POST/curl command that allows uploads without exposing credentials, then saving that command in the local share upload DB.

## Important APIs, types, and functions
- `shareUploadFlags` defines `--recursive`, `--expire`, and `--content-type`.
- `shellQuoteRegex` and `shellQuote` escape shell-special characters in generated curl form values.
- `checkShareUploadSyntax` validates targets, expiry bounds, and requires `--recursive` for prefix targets.
- `makeCurlCmd` builds the actual `curl -F ...` command from POST URL and form fields.
- `saveSharedURL` loads, updates, and saves the upload share DB.
- `doShareUploadURL` calls `ShareUpload`, prints output, and persists it.
- `mainShareUpload` parses flags and loops over targets.

## Control flow
Syntax validation enforces at least one target, parses expiry from `--expire`, limits it to 1 second through 7 days, and checks that targets ending in the client URL separator require recursive mode. Execution initializes local share config, parses expiry/content type, and for each target constructs a client, calls `ShareUpload(ctx, isRecursive, expiry, contentType)`, converts the returned POST form into a curl command, prints a `shareMessage`, and stores it in `uploads.json`.

## State and persistence
Writes generated upload curl commands to the local uploads DB. DB load prunes expired entries. No remote object is created; the remote interaction only creates presigned POST data.

## Dependencies and integration points
Uses MinIO client `ShareUpload`, local share DB/config helpers, global output, and shell quoting helpers. Non-S3 targets surface `APINotImplemented`.

## Risks and edge cases
- Map iteration over `uploadInfo` makes curl form field ordering nondeterministic, though semantically equivalent.
- `postURL` is not shell-quoted, so it assumes the presigned URL returned by the client is already safe as a shell token.
- Recursive mode appends `<NAME>` to the key field, which the UI highlights and users must replace.
- `saveSharedURL` ignores the return from `shareDB.Save`, returning nil even if save fails after `Set`.

## Test signals
`share-upload_test.go` covers `makeCurlCmd` escaping of spaces, quotes, ampersands, angle brackets, pipes, parentheses, backticks, tabs, semicolons, dollar signs, and hash characters. Additional tests should cover expiry validation, recursive prefix validation, and save error propagation.
