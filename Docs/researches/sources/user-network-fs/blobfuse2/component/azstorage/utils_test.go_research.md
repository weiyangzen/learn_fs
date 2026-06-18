# sources/user-network-fs/blobfuse2/component/azstorage/utils_test.go

Purpose: `utils_test.go` is the unit test suite for azstorage utility helpers around content types, access tiers, permissions, client options, endpoint formatting, auth-mode detection, error mapping, path manipulation, and range parsing.

Important APIs, types, and functions: The file defines `utilsTestSuite` and table-driven helper structs for content types, access tiers, file modes, endpoints, and protocols. It tests `getContentType`, `populateContentType`, `getAccessTierType`, `getFileMode`, `getFileModeFromACL`, `sanitizeSASKey`, `sanitizeEtag`, `getAzBlobServiceClientOptions`, `getAzDatalakeServiceClientOptions`, `formatEndpointAccountType`, `formatEndpointProtocol`, `autoDetectAuthMode`, `removeLeadingSlashes`, `storeDatalakeErrToErr`, `removePrefixPath`, and `parseRangeHeader`.

Control flow: Tests are grouped as Testify suite methods. Many are table-driven with `s.Run` subtests. Content type tests first validate fallback behavior, then mutate the global map with JSON and re-query. Endpoint tests exercise standard public cloud endpoints, zonal endpoints, China/Germany/Government clouds, private endpoints, protocol insertion, and intentionally malformed endpoint strings. Error mapping tests synthesize `azcore.ResponseError` values with datalake error codes.

State and persistence behavior: The suite mostly avoids external persistence. It mutates package global `ContentTypes` through `populateContentType`, sets a silent logger for permission parsing tests, and constructs client option objects with transport/proxy settings. No live Azure calls are made.

Dependencies and integration points: Tests depend on Azure SDK `azcore`, `to`, blob access tiers, datalake errors, BlobFuse2 `common` and `log`, Testify, and endpoint/auth types defined elsewhere in the azstorage package. They provide safety signals for helpers consumed by both Blob and ADLS storage implementations.

Risks: Because `ContentTypes` is global, test order or parallelization could leak the `.tst` override into other tests. Some endpoint tests assert preservation of malformed strings as false positives, which documents current behavior but can lock in questionable URI formation. The suite does not test concurrent access to global maps or failure branches in HTTP client construction.

Test signals: Coverage is strong for mapping tables and normal parsing behavior: many extensions including case-insensitive paths, all configured access tiers, ACL mask behavior, auth priority order, prefix stripping, datalake error categories, and valid/invalid byte ranges. Missing signals include blob error mapping, cloud configuration detection, SDK log listener options, metadata folder/symlink parsing, `removePrefixPath` empty-trim panic, and ACL strings missing required fields.
