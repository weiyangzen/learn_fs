# Research: sources/object-store/minio/cmd/bucket-listobjects-handlers.go

Purpose: implements S3 list operations for objects and object versions, including V1, V2, metadata-enriched variants, archive listing, continuation-token proxy handling, argument validation, ETag decryption, and XML response generation.

Important APIs and functions: `validateListObjectsArgs` checks max keys, encoding type, object prefix validity, and marker/prefix compatibility. `ListObjectVersionsHandler` and `ListObjectVersionsMHandler` call `listObjectVersionsHandler`. `ListObjectsV2Handler` and `ListObjectsV2MHandler` call `listObjectsV2Handler`. `ListObjectsV1Handler` handles legacy listing. `parseRequestToken`, `proxyRequestByToken`, and `proxyRequestByNodeIndex` interpret continuation tokens containing node indexes and proxy to remote endpoints when needed.

Control flow: each handler builds context, audits, extracts bucket, verifies object API and authorization, parses query args with helper functions, validates arguments, calls the appropriate `ObjectLayer` list method, decrypts ETags via `DecryptETags`, generates S3 response structs, and writes XML. Metadata variants install `checkObjMeta` closures that re-check request auth per object/action during response generation. V2 additionally supports archive extraction listing when `xMinIOExtract` is true and the prefix includes the archive pattern.

State and persistence behavior: list handlers are read-only from the object namespace perspective. They may proxy requests to another node based on continuation token suffix, and they may consult KMS for encrypted ETag presentation.

Dependencies and integration points: integrates HTTP auth, mux route vars, policy actions, object-layer list APIs, response generators, archive listing, KMS ETag decryption, global proxy endpoints, and distributed node proxying.

Risks: `validateListObjectsArgs` comments mention delimiter constraints but the current code does not enforce delimiter equals `/`, so behavior may differ from comments. Marker must have prefix or returns `ErrNotImplemented`, a compatibility edge. Continuation-token parsing uses `getKeySeparator` and `strconv.Atoi`; malformed suffixes silently become local tokens.

Test signals: this exact file has no dedicated test in the subset. Related bucket handler tests cover multipart upload listing, not object listing. Risks around V2 continuation, metadata authorization, archive listing, and proxying require other test coverage.
