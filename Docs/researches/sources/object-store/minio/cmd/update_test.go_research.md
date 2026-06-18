# sources/object-store/minio/cmd/update_test.go

Validates update release parsing and URL/data helpers. Tests cover official RFC3339 version parsing, release tag conversion including hotfix suffixes, runtime/environment-specific `getDownloadURL`, Helm label parsing from a temporary file, local HTTP-server behavior for `downloadReleaseURL`, and malformed/valid `parseReleaseData` inputs.

State is limited to temporary files, `t.Setenv`, and local `httptest` servers. The tests avoid real update servers and do not execute `verifyBinary` or `commitBinary`.

The strongest signals are release metadata format compatibility and deployment URL behavior. Remaining gaps include User-Agent details, minisign verification, updater concurrency, and binary download memory behavior.
