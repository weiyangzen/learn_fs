<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/handler-utils_test.go -->
# sources/object-store/minio/cmd/handler-utils_test.go

## Purpose
Tests region constraint parsing, metadata extraction, and virtual-host resource construction for shared HTTP handler utilities.

## Important APIs, types, and functions
- `TestIsValidLocationConstraint` exercises `parseLocationConstraint` under valid XML, empty location, malformed XML, and non-XML bodies.
- `TestExtractMetadataHeaders` validates `extractMetadataFromMime` for content type, ignored headers, user metadata prefixes, canonicalization, multiple values, and nil input.
- `TestGetResource` validates `getResource` for virtual-host style domains, IPv6 hosts, IP:port hosts, non-matching domains, and nil domains.

## Control flow
The location test initializes a temporary FS object layer and config region, builds requests with XML bodies or invalid bodies, and compares returned API error codes. Metadata tests pass synthetic headers into extraction and compare maps with `reflect.DeepEqual`. Resource tests call `getResource` with path/host/domain triples and assert the expected path-style resource.

## State and persistence behavior
The location test creates temporary storage/config state through `prepareFS` and `newTestConfig`, then removes the filesystem directory. Other tests are in-memory.

## Dependencies and integration points
Depends on MinIO test storage setup, global server config region, XML marshaling, HTTP headers, textproto MIME headers, and resource/domain logic from `handler-utils.go`.

## Risks and edge cases
Coverage does not include replication header mapping, sensitive metadata deletion, `aws-chunked` trimming, stats wrappers, proxying, or error response routing. Region tests use the default empty region behavior and a configured default region but do not test mismatched non-empty regions beyond expected helper behavior.

## Test signals
Signals are exact API error codes, extracted metadata maps, expected failure for nil metadata input, and exact resource strings for virtual-host and path-style requests.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/handler-utils_test.go -->
