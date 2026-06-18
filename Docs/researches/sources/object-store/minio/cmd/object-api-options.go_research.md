# sources/object-store/minio/cmd/object-api-options.go

## Purpose
This file translates HTTP request headers, query parameters, and metadata maps into `ObjectOptions` for get/head, get-object-attributes, delete, put, copy, and complete-multipart operations. It is the bridge between S3/MinIO request syntax and backend object-layer semantics.

## Important APIs, types, and functions
`getDefaultOpts` parses encryption/proxy/replication/speedtest signals and builds the base `ObjectOptions`, including SSE-C, SSE-C copy source, SSE-S3, and encrypted metadata handling. `getOpts` parses GET/HEAD options such as `partNumber`, `versionId`, delete-marker flags, delete-marker replication-ready checks, tag directive, and bucket versioning/suspension state. `getAndValidateAttributesOpts` builds options for GetObjectAttributes and writes an XML error response on invalid arguments. `parseObjectAttributes`, `parseIntHeader`, and `parseBoolHeader` are reusable parsers.

`delOpts` extends `getOpts` for delete requests by parsing force-delete prefix behavior, adjusting versioning suspension at bucket level, forcing null version IDs for directory objects, parsing source delete marker state, and parsing source modification time. `putOptsFromReq`, `putOpts`, `putOptsFromHeaders`, `copyDstOpts`, and `copySrcOpts` parse PUT and copy options, including version IDs, versioning enablement, source modification time, replication source timestamps, SSE-KMS, SSE-C/SSE-S3, user metadata, and ETag preservation. `completeMultipartOpts` parses source modification time, requested content checksum, SSEC encryption function, replication request metadata, and replication SSEC checksum metadata.

## Control flow
The control flow is layered. Operation-specific functions validate operation-specific query/header values, then delegate to common encryption/default parsers. Version ID parsing trims whitespace and accepts the null version ID but otherwise requires UUID syntax. Attribute validation defers error-response writing until all parsing has failed or succeeded, allowing it to report S3-style argument names and values.

## State and persistence behavior
The file does not persist state itself, but it reads global bucket versioning state and populates options that directly control persistent behavior: whether writes create versions, whether deletes create delete markers, whether directory objects use null versions, whether replication metadata/timestamps are preserved, whether ETags are preserved, and whether multipart completion records checksums or replication actual-size metadata.

## Dependencies and integration points
It depends on HTTP requests/headers, UUID parsing, MinIO crypto and encryption packages, internal checksum parsing, internal HTTP header constants, global bucket versioning state, API error conversion and response writers, metadata constants, and object attribute response types. It is integrated with S3 handlers before they call the `ObjectLayer`.

## Risks and test signals
Risks are concentrated in header parsing and option defaults: permissive or strict bool parsing can change replication/delete behavior, wrong versioning checks can allow invalid version ID writes, and encryption header parsing failures are wrapped differently by PUT paths. `getAndValidateAttributesOpts` writes the HTTP response itself on invalid options, so callers must respect the returned `valid` flag. The local options test covers only object attribute parsing; broader signals come from API handler and object-layer tests.
